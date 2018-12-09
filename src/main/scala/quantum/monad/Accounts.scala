package quantum.monad

import quantum.computing.Monoid

class Accounts[B] extends HistogramMonad[B, Double] {
  val m = new Monoid[Double] {
    override val empty: Double = 0.0
    override val combine: (Double, Double) => Double = _ + _
  }
  override val distributionRule: ((B, Double), List[(B, Double)]) => List[(B, Double)] = {
    case ((b, v), cs) => List((b -> v)) ++ cs
  }
}
