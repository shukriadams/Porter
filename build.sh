rm -rf ./build-out
mkdir -p ./build-out
python3 porter.py --install ./src/Porter
dotnet restore
dotnet publish \
    --configuration Release \
    --runtime linux-x64 \
    -o ./publish \
    -p:PublishReadyToRun=true \
    -p:PublishSingleFile=true \
    -p:PublishTrimmed=true \
    -p:IncludeNativeLibrariesForSelfExtract=true \
    --self-contained true 

./publish/Porter