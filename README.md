# Porter - A Different C# Package Manager

Porter does C# packages in the same way NodeJS, GoLang and others do it - pure source code, fetchable directly from git repos, using JSON manifest files. Packages are linked via recursing namespaces.

## Features 

- Packages can reference their own packages, ad infinitum*. Porter will import and set them up for you. 
- Different versions of a package can be referenced through-out your total package stack without collisions. 

* Depending on how long C# namespaces
 
## Caveats & Limitations

- Packages are confined to Dotnet standard libraries. No Nuget packages, no DLLs.
- Package should not expose types defined in their own packages. Well, they can, and you're free to use them, but it's not safe. Porter namespaces will help you know when you're in the danger zone. Please choose safety.
- Only github repositories are currently supported, and tags are mandatory.
- Packages are pure source - assume the author did a compile check before tagging. 
- It's still a proof-of-concept, and needs polish, but it works (on Linux).

## Use

Create a `porter.json` file in the root of your C# project (the one with the .csproj file in it). This json file works similarly to NodeJS's package.json, and should look like

    {
        "name" : "MyProjectNamespace",
        "runtimes" : [ 6 ],
        "packages" : [
            "github.someuser.somepackage@1.0.0" 
        ]
    }

1 - Name should your project's root namespace. You could call it anything, but the actual root namespace will be easiest.
2 - Runtimes should be Dotnet Runtime your application targets. In this case it's Dotnet 6. 
3 - Packages is an optional string array, and references a public repo on github, at some tag version. These are the packages your project depends on.
4 - The package repos pointed to should each have their own porter.json package in its root, with the same structure above, and should declare a runtime that intersects with yours.

Copy porter.py to your system. Run using

    python porter.py --install /dir/to/your/porter.json

This will create a `porter` directory in your project root. In your code you can do

    using MyProjectNamespace.Porter_Packages.somepackage;

and all types from `somepackage` will now be available. Don't everybody thank me at once.

You should add the `porter` directory to git ignore.

## Don't

Avoid traversing multiple `.Porter_Packages.` in a single reference. That is, if you're using a package that itself uses packages, you can access the sub-packages too, f.ex 

    using MyProjectNamespace.Porter_Packages.somepackage.Porter_Packages.whoknowswhatsdownhere;

If you do this, and `somepackage` changes its own dependencies at some point, you can end up with broken code after you update. 

## Why?

C# has always supported packages as precompiled DLL's. These morphed into nuget packages, but the underlying mechanism is still fundamentally limited. Packages can bring along their own DLLs, they all live in a single flattened assembly cache, and conflicts occur. There's also a high bar of entry to creating packages. They need to live in a nuget repo or similar, and when you're referencing them, it's difficult to see their source, let along change anything from your project.

If you've used NodeJS or similar, you already know you can import packages directly from their source repositories, as plain source code. You can read, step through and even change their code, right in your project, while you code. This makes it easier to fix errors, add changes, even fork on the spot. This is useful if you like to reuse code as discrete packages with  dedicated functions.

## How?

Its all just recursing namespace wrapping, all the way down. Examine the files in `porter` to see for yourself. You're also not trapped in anything. If at some point you want to remove Porter entirely, simply include the code packages in your repo code and commit. You can change the namespace wrappers to whatever you want. 


