using System;

namespace PdfDownloader
{
    public class Program
    {
        private static void Main(string[] args)
        {
            if (args.Length != 1)
            {
                Console.WriteLine("The Usage is App.exe ROOT");
                Console.WriteLine("The File(s) gets downloaded to ROOT/PDF");
                return;
            }
            string PDFDownloadLocation = args[0] + "/PDF";
            AsyncPdfDownloader downloader = new AsyncPdfDownloader(PDFDownloadLocation);

            // As this is an Asynchronous Operation
            // Wait till the Downloaded Flag becomes true
            // This is so that we can halt our code here
            while (!downloader.Downloaded) { }
        }
    }
}
