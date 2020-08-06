using iTextSharp.text.pdf;
using iTextSharp.text.pdf.parser;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;

namespace PdfToCSVParser
{
    public class ParseAD23
    {
        private readonly string FileSourcePDF;
        private readonly string FileDestinationCSV;
        private List<List<string>> ICAOCodes { get; set; }

        public ParseAD23(string FileSourcePDF, string FileDestinationCSV)
        {
            this.FileSourcePDF = FileSourcePDF;
            this.FileDestinationCSV = FileDestinationCSV;
            ICAOCodes = new List<List<string>>();
        }

        public void PerformConversion()
        {
            Console.WriteLine("Starting to Parse");
            ExtractObstacleList();
            // The Hack Performs a Lot of Cleanup on Extracted
            // Obstacle List
            PerformHackAndCleanUpOnObstacleList();
            //DisplayObstacles();
            Console.WriteLine("Writing to CSV");
            WriteToColonSV();
        }

        public void DisplayObstacles()
        {
            foreach (List<string> list_data in ICAOCodes)
            {
                foreach (string obstacle in list_data)
                {
                    Console.Write(obstacle + " : ");
                }
                Console.WriteLine();
            }
        }
        public void WriteToColonSV()
        {
            using (StreamWriter w = new StreamWriter(FileDestinationCSV))
            {
                // Add Colon SV Header to Make it Easier to Understand
                // What Each Column means
                w.WriteLine("Codes:Name");
                foreach (List<string> icaoRow in ICAOCodes)
                {
                    // Write A Colon Separated Row to Document
                    w.WriteLine(icaoRow[1]/*ICAO*/ + ":" + icaoRow[0]/*Name*/);
                    w.Flush();
                }
            }
        }
        public void ExtractObstacleList()
        {
            // Setting this to true will add the required value
            using (PdfReader reader = new PdfReader(FileSourcePDF))
            {
                // Iterate through all the pages
                for (int i = 1; i <= reader.NumberOfPages; i++)
                {
                    TableExtractionStrategy strategy = new TableExtractionStrategy
                    {
                        // Modify this value if Required
                        NextLineLookAheadDepth = 150,
                        NextCharacterThreshold = 1.0F
                    };

                    // Extract the Page Data According to the pre-decided Strategy
                    string page = PdfTextExtractor.GetTextFromPage(reader, i, strategy);
                    // Get A Data Set of All Obstacles from the Given PDF
                    ICAOCodes.AddRange(strategy.GetTable());
                }
            }
        }
        public void PerformHackAndCleanUpOnObstacleList()
        {
            // The Rest is a Hack
            // A Well Designed Hack that works on All Airports

            // Remove All Unrequired Data from the Table
            // This Junk Gets Generated Given it's presence in table's periphery
            // We Know Junk Data here always has a count of 1
            ICAOCodes.RemoveAll(x => x.Count == 1
            && (
            // Rest All Are always present
            // At the Top of the page
            x[0].TrimStart().StartsWith("AD 2 VA")
            || x[0] == ("AIRAC effective date")
            || x[0].TrimStart().StartsWith("Airports Authority of India")
            || x[0].TrimStart().StartsWith("AMDT ")
            || x[0] == "India"
            || x[0].TrimStart().StartsWith("AIP")
            || x[0].TrimStart().StartsWith("AD 1.3-")
            || x[0].TrimStart().StartsWith("AD 1.3 INDEX TO AERODROMES")
            || IsDateOfPDFPublishing(x[0])));

            for (int i = 0; i < ICAOCodes.Count - 1;)
            {
                List<string> table_cur = ICAOCodes[i];
                List<string> table_next = ICAOCodes[i + 1];

                // Take care of Situation When
                // Ozar(Airport Name) is on one line
                // And VAOZ( Code is on next)
                if (table_cur.Count == 1
                    && table_next.Count >= 1)
                {
                    for (int j = 0; j < table_next.Count; ++j)
                    {
                        table_cur.Insert(1 + j, table_next[j]);
                    }
                    ICAOCodes.RemoveAt(i + 1);
                    continue;
                }
                // Use this When One Line has Airport Name: Airport Code
                //OZAR : VAOZ :
                // And Next Line has rest of Data
                //DOM: IFR / VFR : S - NS - P : AD 2 - VAOZ :
                // Verify by checking the Ending of Last parameter
                // Must match the ICAO Code
                if (table_cur.Count == 2
                    && table_next.Count == 4
                    && table_next[3].TrimEnd().EndsWith(table_cur[1]/*ICAO*/))
                {
                    for (int j = 0; j < table_next.Count; ++j)
                    {
                        table_cur.Insert(2 + j, table_next[j]);
                    }
                    ICAOCodes.RemoveAt(i + 1);
                    continue;
                }
                // There Are many cases when
                // The Next Value contains An Extension of the previous value
                // For Example, Hello World This is Vortex
                // Is a long statement that the parser could have
                // considered as a different statement
                // So we need to merge all of them together
                if (table_cur.Count == 6 && table_next.Count == 1 && table_next[0] == table_cur[1])
                {
                    // In case Next Element is Actually Start of a New Value
                    // Which is in improper format
                    table_cur[5] += " " + table_next[0];
                    ICAOCodes.RemoveAt(i + 1);
                }
                else
                {
                    ++i;
                    continue;
                }
            }
            // Trim All Elements
            foreach (List<string> items in ICAOCodes)
            {
                for (int i = 0; i < items.Count; ++i)
                {
                    items[i] = items[i].Trim();
                }
            }
            // Note that we find that every ICAO Element Table Has Count of 6
            // Any Table Element with lesser count is to be removed
            // The Headings also contain 6 Elements
            // Remove this by Passing
            ICAOCodes.RemoveAll(x => x.Count != 6 //6 Columns present
                                                  //Note that Last Column Always ends with the ICAO Code
                || !x[5].EndsWith(x[1])
            );

            foreach (List<string> items in ICAOCodes)
            {
                for (int i = 0; i < items.Count; ++i)
                {
                    // Replace Double Consecutive Spaces by
                    // Single Space

                    items[i] = Regex.Replace(items[i], @"\s+", " ")
                                // Also convert CSIA , Mumbai to CSIA, Mumbai
                                .Replace(" ,", ",").Trim();
                }
            }

            ICAOCodes = ICAOCodes.OrderBy((x => x[1])).ToList();
        }

        // Also read https://docs.microsoft.com/en-us/dotnet/api/system.datetime.tryparseexact
        public static bool IsDateOfPDFPublishing(string val)
        {
            DateTime dt = new DateTime();
            return DateTime.TryParseExact(val.Trim(), "dd MMM yyyy", CultureInfo.InvariantCulture, DateTimeStyles.None, out dt);
        }

    }
}
