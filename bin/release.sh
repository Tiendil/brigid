#!/usr/bin/bash

set -e

export BUMP_VERSION=$1

echo "Bumping version as $BUMP_VERSION"

export BRIGID_VERSION=$(poetry version $BUMP_VERSION --short)
export BRIGID_VERSION_TAG="backend-$BRIGID_VERSION"

echo "New version is $BRIGID_VERSION"
echo "New version tag $BRIGID_VERSION_TAG"

echo "Building Python package"

poetry build

echo "Commit changes"

git add -A
git commit -m "Backend release ${BRIGID_VERSION}"
git push

echo "Create tag"

git tag $BRIGID_VERSION_TAG
git push origin $BRIGID_VERSION_TAG
