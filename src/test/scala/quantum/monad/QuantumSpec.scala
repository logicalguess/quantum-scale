package quantum.monad

import org.scalatest.FlatSpec
import quantum.domain.Complex

class QuantumSpec extends FlatSpec {

  "Hadamard" should "" in {
    val S0 = List("|0>" -> Complex.one, "|1>" -> Complex.zero)
    val S1 = List("|0>" -> Complex.zero, "|1>" -> Complex.one)

    import quantum.domain.Complex.toComplex

    val sq = toComplex(1 / math.sqrt(2))
    val H = Map(
      "|0>" -> List("|0>" -> sq, "|1>" -> sq),
      "|1>" -> List("|0>" -> sq, "|1>" -> -sq)
    )

    val s0 = new Quantum[String]
    val step = s0 >>= H
    println(step(S0))

    assert(step(S0)._1.toSet == Set("|0>" -> sq, "|1>" -> sq))

    val s1 = new Quantum[String]
    val step1 = s1 >>= H
    println(step1(S1))

    assert(step1(S1)._1.toSet == Set("|0>" -> sq, "|1>" -> -sq))
  }
}
