namespace Porter
{
    public class PackageAddress
    {
        
        /// <summary>
        /// currently only public github repos supported
        /// </summary>
        public string Source {get; set; } = "https://github.com";

        public string Repo {get;set;}

        public string Tag {get;set;}
    }
}