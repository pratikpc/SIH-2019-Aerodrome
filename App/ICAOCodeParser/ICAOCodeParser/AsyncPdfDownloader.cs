using System;
using System.ComponentModel;
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
        private readonly string DownloadUri;
        // Store the Destination Folder where we download the PDFs
        private readonly string DestinationFile;
        // Flag which Indicates if the downloading process is in
        // Progress or has completed
        // This is required for verifying Asynchronous Completion
        // We will add a Halting 
        public bool Downloaded { get; set; }

        // Set User Agent for Google Chrome 71
        // Please Note that we Spoof this so that the site thinks we are not a Robot Downloader
        // Which we actually are
        public readonly string UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36";

        public AsyncPdfDownloader(string DownloadUri, string DestinationFile)
        {
            this.DownloadUri = DownloadUri;
            // Set the Destination Directory
            this.DestinationFile = DestinationFile;
            WebClient = new WebClient();
            // Set User Agent for Google Chrome 71
            // Please Note that we Spoof this so that the site thinks we are not a Robot Downloader
            // Which we actually are
            WebClient.Headers.Add("User-Agent", UserAgent);
            // Runs when the File Download is Completed
            WebClient.DownloadFileCompleted += new AsyncCompletedEventHandler((sender, e) =>
            {
                // Set Downloaded as True
                Downloaded = true;
                Console.WriteLine("Completed Download of " + DownloadUri);
            });
            // Runs where the Progress is Changed
            // We can use this to display Messages
            WebClient.DownloadProgressChanged += new DownloadProgressChangedEventHandler((sender, e) =>
                {
                    double bytesIn = double.Parse(e.BytesReceived.ToString());
                    double totalBytes = double.Parse(e.TotalBytesToReceive.ToString());
                    double percentage = bytesIn / totalBytes * 100;
                    Console.WriteLine("Downloaded " + percentage + "%" + " from " + DownloadUri);
                });
            // As the Downloading Process is not complete yet
            Downloaded = false;
            // Start Downloading the First File
            DownloadCurrentFileToRootAsync();
        }
        private void DownloadCurrentFileToRootAsync()
        {
            Uri uri = new Uri(DownloadUri);
            Console.WriteLine("Starting Download of " + uri);
            WebClient.DownloadFileAsync(uri, DestinationFile);
        }
    }
}
