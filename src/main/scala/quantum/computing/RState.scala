package quantum.computing

case class RState[B](bins: List[(B, Double)]) extends UState[RState[B], B, Double] {
  val m = new Monoid[Double] {
    override val empty: Double = 0.0
    override val combine: (Double, Double) => Double = _ + _
  }

  override val distributionRule: ((B, Double), List[(B, Double)]) => List[(B, Double)] = {
    case ((b, v), cs) => cs.map { case (c, u) => (c, u * v) }
  }

  override def create(bins: List[(B, Double)]) = RState(bins)
}
