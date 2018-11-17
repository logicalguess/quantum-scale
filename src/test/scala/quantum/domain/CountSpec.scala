package quantum.domain

import org.scalatest.FlatSpec
import quantum.domain.Gate.{H, Ry, controlled, wire}
import quantum.domain.QState.pure

class CountSpec extends FlatSpec {

  def trunc(x: Double, n: Int) = {
    def p10(n: Int, pow: Long = 10): Long = if (n == 0) pow else p10(n - 1, pow * 10)

    if (n < 0) {
      val m = p10(-n).toDouble
      math.round(x / m) * m
    }
    else {
      val m = p10(n).toDouble
      math.round(x * m) / m
    }
  }

  "count ones" should "single input" in {
    def anglef(bits: Int) = 1 / math.pow(2, bits)

    def ones(i: Int, width: Int): Double = {
      var state = pure(Word.fromInt(2 * i, width))
      for (i <- 0 until width - 1) state = state >>= controlled(i, width - 1, Ry(2*anglef(width)))

      // probability last bit is 1
      state(Word.fromInt(2 * i + 1, width)).norm2
    }

    def probToInt(prob: Double, angle: Double, bits: Int): Int =
      (math.asin(math.sqrt(prob))/angle).round.toInt

    for (w <- 2 to 15) {
      println(w)
      val angle = anglef(w)
      for (i <- 0 until math.pow(2, w - 1).toInt) {
        assert(trunc(ones(i, w), 9) == trunc(math.pow(math.sin(Integer.bitCount(i)*angle), 2), 9))
        assert(Integer.bitCount(i) == probToInt(ones(i, w), angle, w))
      }
    }
  }

  "count ones" should "superposition of all inputs" in {
    def anglef(bits: Int) = 1 / math.pow(2, bits)

    def circuit(width: Int) = {
      var state = pure(Word.fromInt(0, width))
      for (i <- 0 until width - 1) state = state >>= wire(i, H)
      for (i <- 0 until width - 1) state = state >>= controlled(i, width - 1, Ry(2*anglef(width)))
      state
    }

    def probToInt(prob: Double, angle: Double, bits: Int): Int =
      (math.asin(math.sqrt(prob*math.pow(2, bits - 1)))/angle).round.toInt

    def counter(k: Int, angle: Double, bits: Int): Double = math.pow(math.sin(k*angle), 2)/math.pow(2, bits)


    for (n <- 2 to 15) {
      println(n)
      val angle = anglef(n)
      val state = circuit(n)
      val power: Int = math.pow(2, n - 1).toInt
      for (k <- 0 until power) {
        //prob of last bit being 1
        val prob = state(Word.fromInt(2 * k + 1, n)).norm2

        assert(trunc(prob, 9) == trunc(2 * counter(Integer.bitCount(k), angle, n), 9))
        assert(Integer.bitCount(k) == probToInt(prob, angle, n))
      }
    }
  }


  "count consecutive ones" should "single input" in {
    def anglef(bits: Int) = 1 / math.pow(2, bits)

    def consecutiveOnes(i: Int, width: Int): Double = {
      var state = pure(Word.fromInt(2 * i, width))
      for (i <- 0 until width - 2) state = state >>= controlled(Set(i, i + 1), width - 1, Ry(2*anglef(width)))

      // probability last bit is 1
      state(Word.fromInt(2 * i + 1, width)).norm2
    }

    def probToInt(prob: Double, angle: Double, bits: Int): Int =
      (math.asin(math.sqrt(prob))/angle).round.toInt

    for (w <- 2 to 6) {
      println(w)
      val angle = anglef(w)
      for (i <- 0 until math.pow(2, w - 1).toInt) {
        println(Word.fromInt(i, w) + " -> " + probToInt(consecutiveOnes(i, w), angle, w))
      }
    }
  }

  "count consecutive ones" should "superposition of all inputs" in {
    def anglef(bits: Int) = 1 / math.pow(2, bits)

    def circuit(width: Int) = {
      var state = pure(Word.fromInt(0, width))
      for (i <- 0 until width - 1) state = state >>= wire(i, H)
      for (i <- 0 until width - 2) state = state >>= controlled(Set(i, i + 1), width - 1, Ry(2*anglef(width)))
      state
    }

    def probToInt(prob: Double, angle: Double, bits: Int): Int =
      (math.asin(math.sqrt(prob*math.pow(2, bits - 1)))/angle).round.toInt

    for (n <- 2 to 6) {
      println(n)
      val angle = anglef(n)
      val state = circuit(n)
      val power: Int = math.pow(2, n - 1).toInt
      for (k <- 0 until power) {
        //prob of last bit being 1
        val prob = state(Word.fromInt(2 * k + 1, n)).norm2

        println(Word.fromInt(k, n) + " -> " + probToInt(prob, angle, n))
      }
    }
  }
}
