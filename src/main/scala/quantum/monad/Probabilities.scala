package quantum.monad

import quantum.computing.Monoid

class Probabilities[B] extends HistogramMonad[B, Double] {
  val m = new Monoid[Double] {
    override val empty: Double = 1.0
    override val combine: (Double, Double) => Double = _ * _
  }

  override val distributionRule: ((B, Double), List[(B, Double)]) => List[(B, Double)] = {
    case ((b, v), cs) => cs.map { case (c, u) => (c, u * v) }
    //case ((b, v), cs) => List((b -> v)) ++ cs  // both work
  }

  override val normalizeStateRule = { bs: List[(B, Double)] =>
    val sum = bs.map(_._2).foldLeft(0.0)(_ + _)
    if (sum == 1.0) bs else bs.map {
      case (b, v) => (b, v / sum)

    }
  }

}
