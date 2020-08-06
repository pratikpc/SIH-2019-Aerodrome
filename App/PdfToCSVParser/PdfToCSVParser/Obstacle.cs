using System;
using System.Collections.Generic;

namespace PdfToCSVParser
{
    internal class CoOrdinate
    {
        // Measures North South Value
        public string Latitude { get; }
        // Measures East West Value
        public string Longitude { get; }

        // Function to Check if the Given String Represents Longitude
        public static bool IsLongitude(string val)
        {
            // Longitude In PDF
            // Always ends with N or S
            // And Contains .
            return (val.TrimEnd().EndsWith('N') || val.TrimEnd().EndsWith('S'))
                && val.Contains(".");
        }
        // Function to Check if the Given String Represents Latitude
        public static bool IsLatitude(string val)
        {
            // Latitude In PDF
            // Always ends with E or W
            // And Contains .
            return (val.TrimEnd().EndsWith('E') || val.TrimEnd().EndsWith('W'))
                && val.Contains(".");
        }
        // Function to Check if the Given String Represents Longitude and Latitude Combined
        public static bool IsLongitudeLatitudeInCSVForm(string val)
        {
            // Longitude & Latitude Together In PDF
            // Always ends with E or W
            // And Contain 'N' or 'S'
            // And Contains .
            return ((val.Contains('N') || val.Contains('S'))
                && val.Contains(".")
                && (val.TrimEnd().EndsWith('E') || val.TrimEnd().EndsWith('W')));
        }
        public string ConvertToTotalDegreeFromDDMMSS(string source)
        {
            // Sample Input Data is 222043.2N
            // or 731400.8E
            // It's Size is 9
            // First Verify if Size is 9
            // If Not, throw Exception
            if (source.Length != 9)
            {
                throw new ArgumentException("");
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

        // As present in CSV File
        // Sample Coordinate Format is
        // 222043.2N0731400.8E
        // So we need to Split it into
        // Latitude and Longitude
        // Note that the Input Format is in Degree Minute Seconds
        // We Also need to convert it to Total Degrees
        // This is Because Google Earth Likes Total Degrees
        public CoOrdinate(string coordinates)
        {
            int lat_idx = coordinates.IndexOf('N');
            if (lat_idx == -1)
            {
                lat_idx = coordinates.IndexOf('S');
            }

            Latitude = coordinates.Substring(0, lat_idx + 1);
            Longitude = coordinates.Substring(lat_idx + 1, coordinates.Length - lat_idx - 1);//.TrimStart('0');

            // Longitude Usually Starts with a Zero In Front 
            // In The PDF Which is not Useful
            if (Longitude.StartsWith("0"))
            {
                Longitude = Longitude.Substring(1);
            }
            Latitude = ConvertToTotalDegreeFromDDMMSS(Latitude);
            Longitude = ConvertToTotalDegreeFromDDMMSS(Longitude);
        }
    }

    internal class Obstacle
    {
        private string elevation;

        // First Unit
        public string RunwayAreaAffected { get; }
        // Second Unit
        public string ObstacleType { get; }
        // Third Unit
        public CoOrdinate CoOrdinate { get; }
        // Fourth Unit
        public string Elevation { get => elevation; set => elevation = value.Substring(0, value.IndexOf(" FT")); }
        // Fifth Unit
        public string Marking { get; }
        // Sixth Unit
        public string Remarks { get; }

        // Code to Verify if the data is a Given Runway/Area Which is Affected
        public static bool IsRunwayAreaAffected(string val)
        {
            return val.Contains("In circling area and") || val.Contains("TKOF") || val.Contains("APCH");
        }

        // We Know that Elevation always ends with FT
        public static bool IsElevation(string value)
        {
            return value.TrimEnd().EndsWith("FT");
        }

        // Initialise With List<String>
        // Our Table Extracted from PDF Has Each Element in this form
        public Obstacle(List<string> obstacles)
        {
            if (obstacles.Count != 6)
                throw new ArgumentException("Obstacles Must Have 6 Elements");
            RunwayAreaAffected = obstacles[0];
            ObstacleType = obstacles[1];
            CoOrdinate = new CoOrdinate(obstacles[2]);
            Elevation = obstacles[3];
            Marking = obstacles[4];
            Remarks = obstacles[5];
        }
        // Convert to CSV Able Format
        public override string ToString()
        {
            return RunwayAreaAffected + "," + ObstacleType + "," + CoOrdinate.Latitude + "," + CoOrdinate.Longitude + "," + Elevation + "," + Marking + "," + Remarks;
        }
    }
}
