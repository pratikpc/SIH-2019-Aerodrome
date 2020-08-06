using iTextSharp.text;
using iTextSharp.text.pdf.parser;
using System;
using System.Collections.Generic;
using System.Text;

// Credits to https://stackoverflow.com/a/42259989
// StackOverflow user https://stackoverflow.com/users/1070002/shaun
namespace CentreFinder
{
    class TableExtractionStrategy : LocationTextExtractionStrategy
    {
        public float NextCharacterThreshold { get; set; } = 1;
        public int NextLineLookAheadDepth { get; set; } = 200;
        public bool AccomodateWordWrapping { get; set; } = true;

        public List<TableTextChunk> Chunks { get; set; } = new List<TableTextChunk>();

        public override void RenderText(TextRenderInfo renderInfo)
        {
            base.RenderText(renderInfo);
            string text = renderInfo.GetText();
            Vector bottomLeft = renderInfo.GetDescentLine().GetStartPoint();
            Vector topRight = renderInfo.GetAscentLine().GetEndPoint();
            Rectangle rectangle = new Rectangle(bottomLeft[Vector.I1], bottomLeft[Vector.I2], topRight[Vector.I1], topRight[Vector.I2]);
            Chunks.Add(new TableTextChunk(rectangle, text));
        }

        public List<List<string>> GetTable()
        {
            List<List<string>> lines = new List<List<string>>();
            List<string> currentLine = new List<string>();

            float? previousBottom = null;
            float? previousRight = null;

            StringBuilder currentString = new StringBuilder();

            // iterate through all chunks and evaluate 
            for (int i = 0; i < Chunks.Count; i++)
            {
                TableTextChunk chunk = Chunks[i];

                // determine if we are processing the same row based on defined space between subsequent chunks
                if (previousBottom.HasValue && previousBottom == chunk.Rectangle.Bottom)
                {
                    if (chunk.Rectangle.Left - previousRight > 1)
                    {
                        currentLine.Add(currentString.ToString());
                        currentString.Clear();
                    }
                    currentString.Append(chunk.Text);
                    previousRight = chunk.Rectangle.Right;
                }
                else
                {
                    // if we are processing a new line let's check to see if this could be word wrapping behavior
                    bool isNewLine = true;
                    if (AccomodateWordWrapping)
                    {
                        int readAheadDepth = Math.Min(i + NextLineLookAheadDepth, Chunks.Count);
                        if (previousBottom.HasValue)
                        {
                            for (int j = i; j < readAheadDepth; j++)
                            {
                                if (previousBottom == Chunks[j].Rectangle.Bottom)
                                {
                                    isNewLine = false;
                                    break;
                                }
                            }
                        }
                    }

                    // if the text was not word wrapped let's treat this as a new table row
                    if (isNewLine)
                    {
                        if (currentString.Length > 0)
                        {
                            currentLine.Add(currentString.ToString());
                        }

                        currentString.Clear();

                        previousBottom = chunk.Rectangle.Bottom;
                        previousRight = chunk.Rectangle.Right;
                        currentString.Append(chunk.Text);

                        if (currentLine.Count > 0)
                        {
                            lines.Add(currentLine);
                        }

                        currentLine = new List<string>();
                    }
                    else
                    {
                        if (chunk.Rectangle.Left - previousRight > 1)
                        {
                            currentLine.Add(currentString.ToString());
                            currentString.Clear();
                        }
                        currentString.Append(chunk.Text);
                        previousRight = chunk.Rectangle.Right;

                    }
                }
            }

            return lines;
        }

        internal void Clear()
        {
            Chunks.Clear();
        }

        public struct TableTextChunk
        {
            public Rectangle Rectangle;
            public string Text;

            public TableTextChunk(Rectangle rect, string text)
            {
                Rectangle = rect;
                Text = text;
            }

            public override string ToString()
            {
                return Text + " (" + Rectangle.Left + ", " + Rectangle.Bottom + ")";
            }
        }
    }
}
