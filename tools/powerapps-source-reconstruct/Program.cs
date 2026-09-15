using Microsoft.PowerPlatform.PowerApps.Persistence.MsApp;
using Microsoft.PowerPlatform.PowerApps.Persistence.MsApp.Models;
using Microsoft.PowerPlatform.PowerApps.Persistence.MsappPacking;

if (args.Length != 3)
{
    Console.Error.WriteLine("Usage: PowerAppsSourceReconstruct <unpack|pack> <input> <output>");
    return 64;
}

var operation = args[0].ToLowerInvariant();
var inputPath = Path.GetFullPath(args[1]);
var outputPath = Path.GetFullPath(args[2]);

try
{
    var service = new MsappPackingService(
        MsappArchiveFactory.Default,
        MsappReferenceArchiveFactory.Default);

    switch (operation)
    {
        case "unpack":
            await service.UnpackToDirectoryAsync(
                inputPath,
                outputPath,
                new MsappUnpackOptions
                {
                    OverwriteOutput = true,
                    MsaprName = "baseline"
                });
            Console.WriteLine($"Unpacked modern Canvas source to {outputPath}");
            break;

        case "pack":
            await service.PackFromMsappReferenceFileAsync(
                inputPath,
                outputPath,
                new PackedJsonPackingClient
                {
                    Name = "PowerAppsCanvasAppUI",
                    Version = "1.0.0"
                },
                new MsappPackOptions
                {
                    OverwriteOutput = true,
                    EnableLoadFromYaml = true
                });
            Console.WriteLine($"Reconstructed Canvas app at {outputPath}");
            break;

        default:
            Console.Error.WriteLine($"Unknown operation: {args[0]}");
            return 64;
    }

    return 0;
}
catch (Exception exception)
{
    Console.Error.WriteLine(exception);
    return 1;
}
