using HtmlAgilityPack;
using System;
using System.ComponentModel;
using System.IO;
using System.Linq;
using System.Net;

namespace PdfDownloader
{
    // This Entire Downloader is based on Downloading with
    // Presence of ProgressBar
    // https://stackoverflow.com/questions/9459225/asynchronous-file-download-with-progress-bar
    public class AsyncPdfDownloader
    {
        private WebClient WebClient { get; set; }
        // Store List of URIs to Download
        private readonly string[] DownloadURIs;
        // Store the Destination Folder where we download the PDFs
        private readonly string DestinationDir;
        // Index of File being Downloaded Currently
        private int CurrentDownload { get; set; }
        // Flag which Indicates if the downloading process is in
        // Progress or has completed
        // This is required for verifying Asynchronous Completion
        // We will add a Halting 
        public bool Downloaded { get; set; }

        // Set User Agent for Google Chrome 71
        // Please Note that we Spoof this so that the site thinks we are not a Robot Downloader
        // Which we actually are
        public readonly string UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36";

        public readonly string UriWithPDFs = @"https://aim-india.aai.aero/eaip-v2/eAIP/EC-menu-en-GB.html";

        public AsyncPdfDownloader(string DestinationDir)
        {
            DownloadURIs = ParseWebPageForPDFs();
            // Download First File
            CurrentDownload = 0;
            // Set the Destination Directory
            this.DestinationDir = DestinationDir;
            // Create the Destination Directory
            // In case it does not exist
            Directory.CreateDirectory(this.DestinationDir);
            WebClient = new WebClient();
            // Set User Agent for Google Chrome 71
            // Please Note that we Spoof this so that the site thinks we are not a Robot Downloader
            // Which we actually are
            WebClient.Headers.Add("User-Agent", UserAgent);
            // Runs when the File Download is Completed
            WebClient.DownloadFileCompleted += new AsyncCompletedEventHandler((sender, e) =>
            {
                Console.WriteLine("Completed Download of " + DownloadURIs[CurrentDownload]);
                // Go To Next File to Download
                ++CurrentDownload;
                // Add Next File To Download Queue
                DownloadCurrentFileToRootAsync();
            });
            // Runs where the Progress is Changed
            // We can use this to display Messages
            WebClient.DownloadProgressChanged += new DownloadProgressChangedEventHandler((sender, e) =>
                {
                    double bytesIn = double.Parse(e.BytesReceived.ToString());
                    double totalBytes = double.Parse(e.TotalBytesToReceive.ToString());
                    double percentage = bytesIn / totalBytes * 100;
                    Console.WriteLine("Downloaded " + percentage + "%" + " from " + DownloadURIs[CurrentDownload]);
                });
            // As the Downloading Process is not complete yet
            Downloaded = false;
            // Start Downloading the First File
            DownloadCurrentFileToRootAsync();
        }
        private void DownloadCurrentFileToRootAsync()
        {
            // Verify if All Files Have Been Parsed
            if (CurrentDownload >= DownloadURIs.Length && !Downloaded/*If Downloading Still On*/)
            {
                // As the Download Process is Now complete
                Downloaded = true;
                return;
            }
            string currentUri = DownloadURIs[CurrentDownload];
            Uri uri = new Uri(currentUri);

            // Convert the Following URL
            //https://aim-india.aai.aero/eaip-v2/eAIP/EC-AD-2.1VOHS-en-GB.pdf
            // TO EC-AD-2.1VOHS-en-GB.pdf
            string FileName = Path.GetFileName(uri.LocalPath);
            FileName = FileName.Substring(FileName.IndexOf("EC-AD-2.1") + 9/*Length of EC-AD-2.1*/, 4/*ICAO Codes are of 4 Digits Always*/) + ".pdf";
            string FileDest = DestinationDir + '/' + FileName;
            Console.WriteLine("Starting Download of " + uri);
            WebClient.DownloadFileAsync(uri, FileDest);
        }
        // The Default URL is
        // https://aim-india.aai.aero/eaip-v2/eAIP/EC-menu-en-GB.html
        private string[] ParseWebPageForPDFs()
        {
            HtmlWeb web = new HtmlWeb
            {
                UserAgent = UserAgent
            };
            Console.WriteLine("Starting to Download " + UriWithPDFs);
            HtmlDocument htmlDoc = web.Load(UriWithPDFs);
            Console.WriteLine("Starting to Parse " + UriWithPDFs);
            // Extract the List of PDFs with URIs here
            return htmlDoc.DocumentNode.SelectSingleNode("//div[@id='AERODROMESdetails']").SelectNodes("//a[contains(@href,'EC-AD-2.1')]").Select(a => "https://aim-india.aai.aero/eaip-v2/eAIP/" + a.Attributes["href"].Value.Trim()).Where(a => a.EndsWith(".pdf")).ToArray();
        }
    }
}
