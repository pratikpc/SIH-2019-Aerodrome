
using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace CentreFinder
{
    public class MainClass
    {
        // You use it by running
        // App ROOT_DIR
        // It looks for PDFs in ROOT_DIR/PDF
        // It creates Result CSV in ROOT_DIR/CSV
        public static void Main(string[] args)
        {
            //ParseAD212 parser = new ParseAD212("C:/Users/vedan/Desktop/aerodrome/Data/PDF/VAJB.pdf", "C:/Users/vedan/Desktop/aerodrome/DVOTK.csv");
            //// This Performs the parsing operation
            //parser.PerformConversion();
            if (args.Length != 1)
            {
                Console.WriteLine("The Usage is App ROOT_DIR");
                Console.WriteLine(" It looks for PDFs in ROOT_DIR/PDF");
                Console.WriteLine(" It creates Result CSV in ROOT_DIR/CSV");
                return;
            }
            string Root = args[0]/*Get Root Directory*/;

            // The Source Location is at ROOT_DIR/PDF
            string PdfSourceLocation = Root + "/PDF/";
            // The Destination Location is at ROOT_DIR/CSV
            string CSVDestinationLocation = Root + "/CSVCentre/";
            //Extract List of All PDF Files
            string[] pdfs = GetPDFFileNameList(Root);

            // Create the CSV Folder where we will add all CSVs
            // If it does not exist
            Directory.CreateDirectory(CSVDestinationLocation);

            // Creates an Array of tasks that need to be converted
            Task[] conversion_tasks = new Task[pdfs.Length];
            for (int i = 0; i < pdfs.Length; ++i)
            {
                // Get Source PDF Location
                string FileSourcePDF = PdfSourceLocation + pdfs[i];
                // Generate CSV Location
                string FileDestinationCSV = CSVDestinationLocation + ConvertPDFNameToCSV(pdfs[i]);
                // Adds to the Conversion Task List
                conversion_tasks[i] = Task.Factory.StartNew(() =>
                {
                    // Create the Parser
                    ParseAD212 parser = new ParseAD212(FileSourcePDF, FileDestinationCSV);
                    // This Performs the parsing operation
                    parser.PerformConversion();
                    Console.WriteLine("Completed Converting " + FileSourcePDF);
                });
            }
            // Wait till All Conversion Tasks are over
            Task.WaitAll(conversion_tasks);
        }
        // Extract the List of PDFs from the PDF Directory
        private static string[] GetPDFFileNameList(string rootDirectory)
        {
            // Extract the List of File Names
            string[] filenames = (from fullFilename
                        // Use the Given Format to Parse the file out
                        // It is available by following constraints
                        in Directory.EnumerateFiles(rootDirectory + "/PDF", "V*.pdf")
                                  select Path.GetFileName(fullFilename)).ToArray<string>();
            return filenames;
        }
        // Convert PDF File Name to CSV File Name
        private static string ConvertPDFNameToCSV(string pdfName)
        {
            // VAKE.pdf becomes VAKE.csv
            return Path.GetFileNameWithoutExtension(pdfName) + ".CSV";
        }
    }
}
