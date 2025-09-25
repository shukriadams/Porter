# Porter - C# Source Package Manager

Porter does C# packages in the same as NodeJS, GoLang and others - pure source code, fetchable directly from git repos, using JSON manifest files.


## Features 

- Packages can reference their own packages, ad infinitum (*). Porter will import and set them up for you. 
- Different versions of the same package can occur in your dependency stack without collisions.

 
## Caveats & Limitations

- Packages are confined to Dotnet standard libraries. No Nuget packages, no DLLs.
- Packages should not expose types defined in their own packages. Well, they can, and you're free to use them, but it's not safe. Porter namespaces will help you know when you're in the danger zone. Please choose safety.
- Only Github repositories are currently supported, and tags are mandatory.
- Only .cs files are currently supported.
- It's still a proof-of-concept. It needs polish. It's been tested, on Linux.


## Use

Create a `porter.json` file in the root of your C# project (the one with the .csproj file in it). This json file works similarly to NodeJS's package.json, and should look like

    {
        "name" : "MyProjectNamespace",
        "runtimes" : [ 6 ],
        "packages" : [
            "github.someuser.somepackage@1.0.0" 
        ],
        "export" : "files",
    }

1 - `name` should your project's root namespace. You can use anything, but the actual root namespace will be easiest when referencing packages from your code.
2 - `runtimes` should be the Dotnet Runtime your application targets. In this case it's Dotnet 6. 
3 - `packages` is an optional string array, must be public repos on github, and must have tagged releases. These are the packages your project depends on.
4 - `export` is optional, and is adirectory in your package to start exporting files from.
5 - The package repos referenced should each have their own porter.json file in their roots, with the same structure above, and should declare a runtime that intersects with yours.

Copy porter.py to your system. Currently Python 3.8.X is supported. Run using

    python porter.py --install /dir/to/your/porter.json

This will create a `porter` directory in your project root. In your code you can do

    using MyProjectNamespace.Porter_Packages.somepackage;

and all types from `somepackage` will now be available. Don't everybody thank me at once. Don't forget to add the `porter` directory to git ignore.

## Don't

Avoid traversing multiple `.Porter_Packages.` in a single reference. That is, if you're using a package that itself uses packages, you can access the sub-packages too, f.ex 

    using MyProjectNamespace.Porter_Packages.somepackage.Porter_Packages.whoknowswhatsdownhere;

If you do this, and `somepackage` changes its own dependencies at some point, you can end up with broken code after you update. 

## Why?

C# has always supported packages as precompiled DLL's. These morphed into nuget packages, but the underlying mechanism is still awkward. Packages can bring along their own DLLs, they all live in a single flattened assembly cache, and conflicts occur. There's also a high bar of entry to creating packages. They need to live in a nuget repo or similar, and when you're referencing them, it's difficult to see their source, let alone change anything from your project.

If you've used NodeJS or similar, you already know you can import packages directly from git, as plain source code. You can read, step through and even change their code, right in your project, while you code. This makes it easier to fix errors, add changes, even fork on the spot. This is useful if you like to reuse code as discrete packages with dedicated functions.

## How?

Its all just recursing namespace wrapping, all the way down. Examine the files in `porter` to see for yourself. You're also not trapped in anything. If at some point you want to remove Porter entirely, simply include the code packages in your repo code and commit. The namespace wrapping is also simple enough to do manually.


