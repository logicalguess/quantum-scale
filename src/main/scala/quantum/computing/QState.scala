package quantum.computing

import quantum.domain.Complex

case class QState[B](bins: List[(B, Complex)]) extends UState[QState[B], B, Complex] {
  val m = new Monoid[Complex] {
    override val empty: Complex = Complex.zero
    override val combine: (Complex, Complex) => Complex = Complex.plus
  }

  override val distributionRule: ((B, Complex), List[(B, Complex)]) => List[(B, Complex)] = {
    case ((b, v), cs) => cs.map { case (c, u) => (c, u * v) }
  }

  override def create(bins: List[(B, Complex)]) = QState(bins)
}