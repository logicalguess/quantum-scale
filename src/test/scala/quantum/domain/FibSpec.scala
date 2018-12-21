package quantum.domain

import org.scalatest.FlatSpec
import quantum.domain.Gate.{H, ZERO, Ry, controlledRy, controlled, wire}
import quantum.domain.QState.pure

class FibSpec extends FlatSpec {

  "fib" should "work with ZERO" in {

    def fib(n: Int): QState = {
      var state = pure(Word.fromInt(0, n))
      for (i <- 0 until n) state = state >>= wire(i, H)
      for (i <- 0 until n - 1)  state = state >>= controlled(i, i + 1, ZERO)

      state
    }

    for (n <- 1 to 10) {
      val q = fib(n)
      val states = q.bins
      println(s"F($n) = ${states.size}")
    }
  }

  "fib" should "work with controlled Ry" in {

    def fib(n: Int): QState = {
      var state = pure(Word.fromInt(0, n))
      for (i <- 0 until n) state = state >>= wire(i, Ry(math.Pi/2))
      for (i <- 0 until n - 1)  state = state >>= controlledRy(i, i + 1, -math.Pi/2)

      state
    }

    for (n <- 1 to 10) {
      val q = fib(n)
      val states = q.bins.filter({ case (w, a) => a.norm2 > 0.0000000000000000000000000000001 })
      println(s"F($n) = ${states.size}")
    }
  }
}
