package quantum.monad

import quantum.computing.Monoid

trait HistogramMonad[B, V] extends ComponentMonad[B => List[(B, V)], List[(B, V)], Unit] {
  protected val m: Monoid[V]

  protected val normalizeStateRule: List[(B, V)] => List[(B, V)] = identity

  protected val combineBinsRule: List[(B, V)] => List[(B, V)] = { bs =>
    bs.groupBy(_._1).toList.map {
      case (b, vs) => (b, vs.map(_._2).foldLeft(m.empty)(m.combine))
    }
  }
  protected val distributionRule: ((B, V), List[(B, V)]) => List[(B, V)]

  override def logic: PartialFunction[(B => List[(B, V)], List[(B, V)]), List[(B, V)]] = {
    case (change, state) => {
      val updates: List[(B, V)] = state.flatMap({ case (b, v) => distributionRule((b, v), change(b)) })
      normalizeStateRule(combineBinsRule(updates))
    }
  }

  override def transformer: Function[List[(B, V)], Unit] = _ => () // random bucket from distribution
}
