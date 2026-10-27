"""Create the ECR repository and GitHub OIDC role using an existing AWS login."""

import json
from pathlib import Path
import subprocess

ACCOUNT = "429502077256"
REGION = "eu-north-1"
REPOSITORY = "networksecurity"
ROLE = "networksecurity-github-ecr-push"
PROVIDER = f"arn:aws:iam::{ACCOUNT}:oidc-provider/token.actions.githubusercontent.com"
HERE = Path(__file__).resolve().parent


def aws(*args, missing=None):
    result = subprocess.run(
        ["aws", *args, "--region", REGION, "--output", "json", "--no-cli-pager"],
        text=True,
        capture_output=True,
    )
    if result.returncode:
        if missing and f"({missing})" in result.stderr:
            return None
        raise RuntimeError(result.stderr.strip())
    return json.loads(result.stdout) if result.stdout.strip() else {}


def main():
    caller = aws("sts", "get-caller-identity")
    if caller["Account"] != ACCOUNT:
        raise RuntimeError(f"Expected account {ACCOUNT}; logged into {caller['Account']}")

    provider = aws(
        "iam", "get-open-id-connect-provider",
        "--open-id-connect-provider-arn", PROVIDER, missing="NoSuchEntity",
    )
    if provider is None:
        aws(
            "iam", "create-open-id-connect-provider",
            "--url", "https://token.actions.githubusercontent.com",
            "--client-id-list", "sts.amazonaws.com",
        )
        print("Created GitHub OIDC identity provider")
    elif "sts.amazonaws.com" not in provider["ClientIDList"]:
        raise RuntimeError("Existing GitHub OIDC provider lacks audience sts.amazonaws.com")

    repository = aws(
        "ecr", "describe-repositories", "--repository-names", REPOSITORY,
        missing="RepositoryNotFoundException",
    )
    if repository is None:
        aws(
            "ecr", "create-repository", "--repository-name", REPOSITORY,
            "--image-tag-mutability", "IMMUTABLE",
            "--image-scanning-configuration", "scanOnPush=true",
        )
        print(f"Created ECR repository {REPOSITORY} in {REGION}")

    trust_file = HERE / "trust-policy.json"
    trust = json.loads(trust_file.read_text())
    role = aws("iam", "get-role", "--role-name", ROLE, missing="NoSuchEntity")
    if role is None:
        aws(
            "iam", "create-role", "--role-name", ROLE,
            "--description", "GitHub main branch may publish networksecurity images to ECR",
            "--assume-role-policy-document", f"file://{trust_file}",
        )
        print(f"Created IAM role {ROLE}")
    elif role["Role"]["AssumeRolePolicyDocument"] != trust:
        raise RuntimeError(f"Existing role {ROLE} has another trust policy; review it before changing")

    aws(
        "iam", "put-role-policy", "--role-name", ROLE,
        "--policy-name", "PushNetworkSecurityEcr",
        "--policy-document", f"file://{HERE / 'ecr-push-policy.json'}",
    )
    print(f"Ready: arn:aws:iam::{ACCOUNT}:role/{ROLE}")
    print(f"Registry: {ACCOUNT}.dkr.ecr.{REGION}.amazonaws.com/{REPOSITORY}")
    print("Commit and push the workflow to main to build, verify, and publish the image.")


if __name__ == "__main__":
    main()
