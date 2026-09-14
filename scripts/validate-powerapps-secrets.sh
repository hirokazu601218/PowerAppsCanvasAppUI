#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${TEST_EMAIL:-}" ]]; then
  echo "Missing GitHub Actions secret: POWERAPPS_TEST_USER_EMAIL" >&2
  exit 1
fi

case "${MS_AUTH_CREDENTIAL_TYPE:-password}" in
  password)
    if [[ -z "${TEST_PASSWORD:-}" ]]; then
      echo "Missing GitHub Actions secret: POWERAPPS_TEST_USER_PASSWORD" >&2
      exit 1
    fi
    ;;
  certificate)
    if [[ -z "${TEST_CERT_BASE64:-}" ]]; then
      echo "Missing GitHub Actions secret: POWERAPPS_TEST_CERT_BASE64" >&2
      exit 1
    fi
    ;;
  *)
    echo "POWERAPPS_AUTH_MODE must be password or certificate" >&2
    exit 1
    ;;
esac

echo "Authentication settings are present. Secret values were not printed."
