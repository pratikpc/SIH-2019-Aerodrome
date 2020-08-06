using iTextSharp.text.pdf;
using iTextSharp.text.pdf.parser;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;

namespace CentreFinder
{
    public class ParseAD212
    {
        private readonly string FileSourcePDF;
        private readonly string FileDestinationCSV;
        private List<List<string>> ICAOCodes { get; set; }

        public static string ConvertToTotalDegreeFromDDMMSS(string source)
        {
            source = source.Trim();
            // Sample Input Data is 222043.2N
            // or 731400.8E
            // It's Size is 9
            // First Verify if Size is 9
            // If Not, throw Exception
            if (source.Length != 10 && source.Length != 9)
            {
                throw new ArgumentException("ew" + source.Length + ' ' + source);
            }

            // Now We know
            // South and West Imply Negative
            // And Sign is Placed at the very end
            double sign = (source.EndsWith('S') || source.EndsWith('W')) ? -1 : 1;

            // Now that Use of N or W is Done
            // Remove it
            source = source.Substring(0, source.Length - 1/*Count till 2nd Last*/);

            // Now look at the Conversion Format
            // First Two Digits represent Degrees
            // Next Two Represent Minutes 
            // Rest Represent Seconds
            double degree = double.Parse(source.Substring(0, 2/*Count*/));
            double minute = double.Parse(source.Substring(2, 2/*Count*/));
            double second = double.Parse(source.Substring(4/* Till End*/));
            double total_degree = degree + minute / 60 + second / 3600;
            return total_degree.ToString();
        }
        // Function to Check if the Given String Represents Longitude and Latitude Combined
        public static bool IsLongitudeLatitudeInCSVForm(string val)
        {
            // Longitude & Latitude Together In PDF
            // Always ends with E or W
            // And Contain 'N' or 'S'
            // And Contains .
            return ((val.TrimEnd().EndsWith('N') || val.TrimEnd().EndsWith('S'))
                || (val.TrimEnd().EndsWith('E') || val.TrimEnd().EndsWith('W'))) 
                && val.Contains(".");
        }
        public ParseAD212(string FileSourcePDF, string FileDestinationCSV)
        {
            this.FileSourcePDF = FileSourcePDF;
            this.FileDestinationCSV = FileDestinationCSV;
            ICAOCodes = new List<List<string>>();
        }

        public void PerformConversion()
        {
            Console.WriteLine("Starting to Parse" + FileSourcePDF);
            ExtractObstacleList();
            // The Hack Performs a Lot of Cleanup on Extracted
            // Obstacle List
            PerformHackAndCleanUpOnObstacleList();
            //DisplayObstacles();
            //Console.WriteLine("Writing to CSV");
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
                w.WriteLine("Latitude,Longtitude,Width,TBearing");
                foreach (List<string> icaoRow in ICAOCodes)
                {
                    var split = icaoRow[4].Replace("N0","N 0").Split(" 0");
                    Console.WriteLine(icaoRow[0] + ';' + split.Length);
                    // Write A Colon Separated Row to Document
                    w.WriteLine(ConvertToTotalDegreeFromDDMMSS(split[0])/*Lat*/ +
                        ',' + ConvertToTotalDegreeFromDDMMSS(split[1]) /*Lon*/+ ',' +
                        icaoRow[2]/*Width*/ + ',' + icaoRow[1]);
                    w.Flush();
                }
            }
        }
        public void ExtractObstacleList()
        {
            // Setting this to true will add the required value
            using (PdfReader reader = new PdfReader(FileSourcePDF))
            {
                bool add = false;
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
                    if (!add && page.Contains("AD 2.12"))
                        add = true;
                    if (add)
                        ICAOCodes.AddRange(strategy.GetTable());
                    if (add && page.Contains("AD 2.13"))
                    {
                        add = false;
                        break;
                    }
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

            // Remove All Unrequired Data from the Table
            // This Junk Gets Generated Given it's presence in table's periphery
            // We Know Junk Data here always has a count of 1
            ICAOCodes.RemoveAll(x => x.Count == 1
            && (x[0] == "In Approach/Take-off/Circling Area and at AD"
            || x[0] == "123456"/*Table Heading Index*/
            // Rest All Are always present
            // At the Top of the page
            || x[0].TrimStart().StartsWith("AD 2 V")
            || x[0] == ("AIRAC effective date")
            || x[0].TrimStart().StartsWith("Airports Authority of India")
            || x[0].TrimStart().StartsWith("AMDT ")
            || x[0] == "India"
            || x[0].TrimStart().StartsWith("AIP")
            || IsDateOfPDFPublishing(x[0])));

            for (int i = 0; i < ICAOCodes.Count - 1;)
            {
                List<string> table_cur = ICAOCodes[i];
                List<string> table_next = ICAOCodes[i + 1];
                table_cur.Remove(" ");
                if (table_cur.Count == 4 && !table_cur[1].TrimEnd().EndsWith("DEG"))
                {
                    table_cur.Insert(2, "");
                    continue;
                }
                if (table_cur.Count == 4 && table_next.Count == 2)
                {
                    table_cur[3] += " " + table_next[0];
                    table_cur.Insert(4 ,table_next[1]);
                    ICAOCodes.RemoveAt(i + 1);
                    continue;
                }
                if (table_cur.Count == 5 && table_next.Count == 1
                    && (IsLongitudeLatitudeInCSVForm(table_next[0])
                    || table_next[0].TrimStart().StartsWith("RWY END")))
                {
                    // In case Next Element is Actually Start of a New Value
                    // Which is in improper format
                    table_cur[4] += " " + table_next[0];
                    ICAOCodes.RemoveAt(i + 1);
                    continue;
                }
                else
                {
                    ++i;
                    continue;
                }
            }


            // Note that we find that every ICAO Element Table Has Count of 6
            // Any Table Element with lesser count is to be removed
            // The Headings also contain 6 Elements
            // Remove this by Passing
            ICAOCodes.RemoveAll(x => x.Count != 5 //5 Columns present
                                                  //Note that Last Column Always ends with the ICAO Code
                || !IsLongitudeLatitudeInCSVForm(x[4]) || x[2] == ""
            );
            // Trim All Elements
            foreach (List<string> items in ICAOCodes)
            {
                for (int i = 0; i < items.Count; ++i)
                {
                    items[i] = items[i].Trim();
                }
                items[1] = items[1].Substring(0, items[1].IndexOf(" DEG"));
                items[4] = items[4].Substring(items[4].IndexOf(':')+1).Trim();
                items[4] = items[4].Substring(0, items[4].IndexOf('E') + 1).Trim();
                items[2] = items[2].Substring(items[2].IndexOf(" x ") + 2).Trim('M').Trim();
            }
            foreach (var codes in ICAOCodes)
            {
                foreach (var code in codes)
                {
                    Console.Write(code + "\t;");
                }
                Console.WriteLine(FileDestinationCSV);
            }

            //foreach (List<string> items in ICAOCodes)
            //{
            //    for (int i = 0; i < items.Count; ++i)
            //    {
            //        // Replace Double Consecutive Spaces by
            //        // Single Space

            //        items[i] = Regex.Replace(items[i], @"\s+", " ")
            //                    // Also convert CSIA , Mumbai to CSIA, Mumbai
            //                    .Replace(" ,", ",").Trim();
            //    }
            //}

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
