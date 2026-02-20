using Bonsai;
using System;
using System.ComponentModel;
using System.Linq;
using System.Reactive.Linq;


[Description("Draws a random number from a geometric distribution.")]
public class DrawFromGeometric : Source<int>
{
    private double p = 0.5;
    public double P
    {
        get { return p; }
        set { p = value; }
    }

    private Random random = new Random();

    public Random Random {
        get { return random; }
        set { random = value; }
    }

    private int maxIter = 1000;

    private int Sample(){

        if (p < 0 || p > 1)
        {
            throw new ArgumentOutOfRangeException("p", "The probability must be between 0 and 1.");
        }
        int i = 1;
        double cdf = 0;
        double target = random.NextDouble();
        while (i < maxIter)
        {
            cdf += Math.Pow(1.0 - p, i - 1.0) * p;
            if (target < cdf)
            {
                break;
            }
            i++;
        }
        return i;

    }

    public override IObservable<int> Generate()
    {
        return Observable.Return(Sample());
    }

    public IObservable<int> Generate<TSource>(IObservable<TSource> source)
    {
        return source.Select(_ => {return Sample();});
    }

}
