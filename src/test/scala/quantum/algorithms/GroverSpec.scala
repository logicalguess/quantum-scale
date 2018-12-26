package quantum.algorithms

import org.scalatest.FlatSpec
import quantum.domain.{S1, Word}
import quantum.domain.QState._
import quantum.algorithms.Grover._


class GroverSpec extends FlatSpec {
  "inv" should "compare" in {

    for (i <- 1 to 100) {
      val bits = (math.log(i) / math.log(2)).toInt + 1
      val w = Word.fromInt(i, bits)

      val state = pure(w) >>= refl(bits)
      val state1 = pure(Word(w.letters ++ List(S1))) >>= inv((0 to w.letters.size - 1).toList) _

      assert(state1.bins.map({ case (w, a) => (Word(w.letters.take(bits)).label, a.toString) }).toMap == state.bins.map({ case (w, a) => (w.label, a.toString)}).toMap)
    }
  }
}
