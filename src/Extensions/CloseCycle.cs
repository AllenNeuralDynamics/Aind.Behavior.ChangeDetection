using Bonsai;
using System;
using System.ComponentModel;
using System.Linq;
using System.Reactive.Linq;

[Combinator]
[WorkflowElementCategory(ElementCategory.Combinator)]
[Description(
    "Emits every element in a finite input sequence, then emits the first " +
    "element once more to close the cycle."
)]
public class CloseCycle
{
    public IObservable<TElement> Process<TElement>(
        IObservable<TElement> source)
    {
        return source
            .ToArray()
            .SelectMany(elements =>
                elements.Length == 0
                    ? elements
                    : elements.Concat(new[] { elements[0] }));
    }
}