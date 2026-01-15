#! /bin/bash

set -e

PUSH=0
TEST=0
BUILD=1
ALLOWED_RUNTIMES=("linux-x64" "win-x64")
RUNTIME="linux-x64"
HASH=""

while [ -n "$1" ]; do 
    case "$1" in
    --push|-p) PUSH=1 ;;
    --test|-t) TEST=1 ;;
    --nobuild) BUILD=0 ;;
    --runtime|-r) RUNTIME="${2#*=}" ;;
    --tag) TAG="${2#*=}" ;;
    esac 
    shift
done

if [ -z "$TAG" ]; then
    echo "tag not explicitly set, trying to get hash+tag from git ..."
    TAG=$(git describe --tags --abbrev=0)
    HASH=$(git rev-parse --short HEAD)
fi

if [ -z "$TAG" ]; then
    echo "TAG not set, exiting"
    exit 1;
fi

echo "tag: ${TAG}"
echo "runtime: ${RUNTIME}"
echo "build: ${BUILD}"
echo "test: ${TEST}"
echo "push: ${PUSH}"

IS_IN_ARRAY=$(echo ${ALLOWED_RUNTIMES[@]} | grep -o $RUNTIME | wc -w)
if [ $IS_IN_ARRAY -eq 0 ]; then
    echo "runtime ${RUNTIME} is not supported"
    exit 1;
fi

# write hash + tag to currentVersion.txt in source, this will be displayed by web ui
echo "$HASH $TAG" > ./src/currentVersion.txt 

if [ $BUILD -eq 1 ]; then
    cd ..
    python3 porter.py --install ./src/Porter
    dotnet restore
    dotnet publish \
        --configuration Release \
        --runtime $RUNTIME \
        -o ./publish \
        -p:PublishReadyToRun=true \
        -p:PublishSingleFile=true \
        -p:PublishTrimmed=true \
        -p:IncludeNativeLibrariesForSelfExtract=true \
        --self-contained true 
    cd -
fi

if [ $TEST -eq 1 ]; then
    echo "testing ... "
    
    ./../publish/Porter

    echo "test passed if reached"
fi


if [ $PUSH -eq 1 ]; then

    echo "uploading to github"
    repo="shukriadams/porter"
    name="porter_${RUNTIME}"
    

    if [ $RUNTIME = "linux-x64" ] ; then
        filename=./../publish/porter
    elif [ $RUNTIME = "win-x64" ] ; then
        filename=./../publish/porter.exe
    fi

    GH_REPO="https://api.github.com/repos/$repo"
    GH_TAGS="$GH_REPO/releases/tags/$TAG"
    AUTH="Authorization: token $GH_TOKEN"
    WGET_ARGS="--content-disposition --auth-no-challenge --no-cookie"
    CURL_ARGS="-LJO#"

    # Validate token.
    curl -o /dev/null -sH "$GH_TOKEN" $GH_REPO || { echo "Error : token validation failed";  exit 1; }

    # Read asset tags.
    response=$(curl -sH "$GH_TOKEN" $GH_TAGS)

    # Get ID of the asset based on given filename.
    eval $(echo "$response" | grep -m 1 "id.:" | grep -w id | tr : = | tr -cd '[[:alnum:]]=')
    [ "$id" ] || { echo "Error : Failed to get release id for tag: $TAG"; echo "$response" | awk 'length($0)<100' >&2; exit 1; }

    # upload file to github
    GH_ASSET="https://uploads.github.com/repos/$repo/releases/$id/assets?name=$(basename $name)"
    curl --data-binary @"$filename" -H "Authorization: token $GH_TOKEN" -H "Content-Type: application/octet-stream" $GH_ASSET

fi  
