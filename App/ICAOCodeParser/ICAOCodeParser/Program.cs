using PdfDownloader;
using PdfToCSVParser;
using System;
using System.IO;

namespace ICAOCodeParser
{
    internal class Program
    {

        private static void Main(string[] args)
        {
            if (args.Length != 1)
            {
                Console.WriteLine("The Usage is App ROOT_DIR");
                Console.WriteLine(" It Downloads ICAO PDF in ROOT_DIR");
                Console.WriteLine(" It Stores ICAO CSV in ROOT_DIR");
                return;
            }
            string Root = args[0];
            string url = @"https://aim-india.aai.aero/eaip-v2/eAIP/EC-AD-1.3-en-GB.pdf";
            string DownloadPDF = Root + "/ICAO.pdf";
            // Provides Colon Separated Values as Airport Names have Commas Themselves
            string ConvertCSV = Root + "/ICAO.colonsv";
            // Creates the Directory at the Specified Location
            Directory.CreateDirectory(Root);
            // Start Downloading From Specified URL
            AsyncPdfDownloader downloader = new AsyncPdfDownloader(url, DownloadPDF);
            // Halt till Download Conversion
            while (!downloader.Downloaded) { }
            // Perform PDF to CSV Conversion
            ParseAD23 parser = new ParseAD23(DownloadPDF, ConvertCSV);
            parser.PerformConversion();
        }
    }
}
