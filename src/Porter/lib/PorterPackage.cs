namespace Porter
{
    public class PorterPackage
    {
        public string name {get;set;}
        public string[] runtimes {get;set;} = new string[] {};
        public string[] packages {get;set;} = new string[] {};
        public string export {get;set;}
        public string[] ignore {get;set;} = new string[] {};

        /// <summary>
        /// Used internally. datetime package was installed
        /// </summary>
        public string __installed {get;set;}
    }
}