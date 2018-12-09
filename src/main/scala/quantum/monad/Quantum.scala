package quantum.monad

import quantum.computing.Monoid
import quantum.domain.Complex

class Quantum[B] extends HistogramMonad[B, Complex]  {
  val m = new Monoid[Complex] {
    override val empty: Complex = Complex.zero
    override val combine: (Complex, Complex) => Complex = Complex.plus
  }

  override val distributionRule: ((B, Complex), List[(B, Complex)]) => List[(B, Complex)] = {
    case ((b, v), cs) => cs.map { case (c, u) => (c, u * v) }
  }
}
