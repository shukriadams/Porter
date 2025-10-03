# Porter - C# Source Package Manager

Porter is a source-only package system for C#. It works in much the same way as NPM for Javascript and Crate for Rust - pure source code, fetchable directly from git repos, using JSON manifest files.


## Features 

- Packages can reference their own packages, ad infinitum (*). Porter will import and set them up for you. 
- Different versions of the same package can occur in your dependency stack without collisions.

 
## Caveats & Limitations

- Packages must rely on Dotnet standard libraries only. Packages cannot pull in Nuget packages, DLLs or any external assemblies.
- Only .cs files are supported.
- Packages should avoid exposing (leaking) types defined by their own dependencies. Technially they can, and you're free to use them, but it's not safe (Porter namespaces will help you identiy when you're in the danger zone, see later). Choose safety.
- Only Github repositories are currently supported.
- Git tags are mandatory - Porter will not sync at the repo or branch level.
- It's still a proof-of-concept, hacked together in Python for now. It needs polish, but it works.

## Use

Create a `porter.json` file in the root of your repo. If you're familiar with NodeJS, this file works similarly to `package.json`. It contents should look like

    {
        "name" : "MyProjectNamespace",
        "runtimes" : [ 6 ],
        "packages" : [
            "github.someuser.somepackage@1.0.0" 
        ],
        export : '/packageFiles',
        ignore : [
            "**/tests/**
        ]
    }

- `name` should be your project's root namespace. You can use anything, but the actual root namespace will be easiest.
- `runtimes` should be the Dotnet Runtimes your application works on. In this case it's Dotnet 6. You can add several. 
- `packages` is an optional string array, must be public repos on github, and must have tagged releases. These are the packages your project depends on.
- The package repos referenced should be Porter packages too (have a valid porter.json file in their repo root), and should declare a runtime that intersects with yours.
- `export` is optional, and is the directory in your package to export files from. Use if this project is a Porter package. If not set, all cs files in the repo will be exported.
- `ignore` is optional array of paths in your package that should not be exposed, use this to hide internal stuff like unit tests, utilities etc. Strings should be standard unix-style globs (git-style format won't work).


Copy porter.py to your system. Currently Python 3.8.X is supported. Run using

    python porter.py --install /dir/to/your/porter.json

This will create a `porter` directory in your project root. In your code you can do

    using MyProjectNamespace.Porter_Packages.somepackage;

and all types from `somepackage` will be available to use. Don't everybody thank me at once.

## Donts

Avoid traversing multiple `.Porter_Packages.` in a single reference. That is, if you're using a package that itself uses Porter packages, you can access the sub-packages too, f.ex 

    using MyProjectNamespace.Porter_Packages.somepackage.Porter_Packages.whoknowswhatsdownhere;

If you do this, and `somepackage` changes its own dependencies at some point, you can end up with broken code after you update. 


## Why?

C# has always done packages as precompiled DLL's. These morphed into nuget packages, but the underlying mechanism is still awkward. Packages can bring along their own DLLs, they all live in a single flattened assembly cache, conflicts and all. There's also a high bar of entry to creating packages. They need to live in a nuget repo or similar, and when you're referencing them, it's difficult to see their source, let alone change anything from your project.

If you've used NodeJS or similar, you already know you can import packages directly from git, as plain source code. You can read, step through and even change their code, right in your project, while you code. This makes it easier to fix errors, try new ideas, even fork on the spot. This is particularly useful if you like to reuse your own code as discrete packages with dedicated functions.


## How?

Its all just recursing namespace wrapping, all the way down. Examine the files in `porter` to see for yourself. You're also not trapped in Porter. If at some point you want to remove it entirely, simply include the code packages in your repo code and commit. The namespace wrapping is also simple enough to do manually, so if the Porter script breaks on you, you can easily fake it on your own. 
