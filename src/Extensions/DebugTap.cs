using Bonsai;
using System;
using System.ComponentModel;
using System.IO;
using System.Reactive.Linq;

[Combinator]
[WorkflowElementCategory(ElementCategory.Combinator)]
[Description("Pass-through diagnostic operator that writes each observed value to a text file.")]
public class DebugTap
{
    [Description("Stage label written with every item.")]
    public string Label { get; set; } = "DBG";

    [Description("Output text file. Use an absolute path for reliable headless runs.")]
    public string FileName { get; set; } = @"C:\BonsaiDataDoC\debug_image_stream.txt";

    public IObservable<TSource> Process<TSource>(IObservable<TSource> source)
    {
        return source.Do(value =>
        {
            var dir = Path.GetDirectoryName(FileName);
            if (!string.IsNullOrEmpty(dir))
            {
                Directory.CreateDirectory(dir);
            }

            File.AppendAllText(
                FileName,
                string.Format(
                    "{0:o},{1},{2}{3}",
                    DateTime.Now,
                    Label,
                    value == null ? "<null>" : value.ToString(),
                    Environment.NewLine));
        });
    }
}