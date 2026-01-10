using Porter.Porter_Packages.Madscience_CommandLineSwitches;

namespace Porter
{
    class Program
    {
        static void Main(string[] args)
        {
            try 
            {
                CommandLineSwitches switches = new CommandLineSwitches(args);

                Console.WriteLine("Porter, a package manager for C#");

                if (switches.InvalidArguments.Any())
                {
                    Console.WriteLine("ERROR : invalid switch(es):");
                    foreach(var r in switches.InvalidArguments)
                        Console.WriteLine(r);

                    System.Environment.Exit(1);
                }
                
                bool hasCommand = false;

                if (!hasCommand || switches.Contains("help") || switches.Contains("h"))
                {
                    hasCommand = true;
                    Console.WriteLine("Usage:");
                    Console.WriteLine("");
                    Console.WriteLine("--help |-h : this help message");
                    Console.WriteLine("--install | -i <optional PATH> : installs Porter packages.");
                    Console.WriteLine("    <PATH> is optional directory where Porter packages will be installed. ");
                    Console.WriteLine("    If no directory is given, the current working directory is used.");
                    Console.WriteLine("    The directory used must contain a valid porter.json file.");
                }

            }
            catch (Exception ex)
            {
                Console.WriteLine(ex);
            }
        }
    }
}