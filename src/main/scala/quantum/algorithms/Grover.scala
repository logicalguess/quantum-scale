package quantum.algorithms

import quantum.domain._
import quantum.domain.QState._
import quantum.domain.Gate._

object Grover {

  def oracleL(f: Int => Boolean)(q_in: List[Int], q_out: Int)(s: Word): QState = {
    val letters = s.letters

    val sub = letters.indices.collect { case i if q_in.contains(i) => letters(i) }.toList
    val x = Word.toInt(Word(sub))

    val a = letters(q_out) == S1
    val fx = if (a ^ f(x))  S1 else S0

    val state = pure(Word(letters.updated(q_out, fx)))
    state
  }

  def oracle(f: Int => Boolean)(s: Word): QState = 
    oracleL(f)((0 to s.letters.size - 2).toList, s.letters.size - 1)(s)

  def refl(width: Int) = {
    var s = pure(Word.fromInt(0, width))
    for (j <- (0 to width))
      s = s >>= wire(j, H)

    (s >< s) * 2.0 - I
  }

  def invL(qs: List[Int])(s: QState): QState = {
    val size = qs.size
    var state = s
    for (j <- (0 to size - 1))
      state = state >>= wire(qs(j), H) _ >>= wire(qs(j), X)


    state = state >>= controlled((0 to size - 2).map(qs).toSet, qs(size - 1), Z)
    for (j <- (0 to size - 1))
      state = state >>= wire(qs(j), X) _ >>= wire(qs(j), H)

    -state
  }

  def inv(s: Word): QState =
    invL((0 to s.letters.size - 2).toList)(pure(s))

  def grover(f: Int => Boolean)(width: Int): QState = {
    val r = (math.Pi * math.sqrt(math.pow(2, width)) / 4).toInt
    var state = pure(Word(List.fill(width)(S0) ++ List(S1)))

    for (j <- (0 to width))
      state = state >>= wire(j, H)

    printState(state)

    for (i <- 1 to r) {
      state = state  >>= oracle(f) _ >>= inv _
      println("\nIteration " + i)
      printState(state)
    }
    -state
  }

  def printChart[K](hist: Map[K, Double]) {
    def pad(str: String, n: Int): String =
      if (str.length > n) str.substring(0, n) else str + (" " * (n - str.length))

    if (hist.nonEmpty) {
      val keyLen = hist.keys.map(_.toString.length).max
      hist.toSeq.map {
        case (h, prob) =>
          pad(h.toString, keyLen).mkString + " " +
            pad(prob.toString, 6) + " " +
            ("#" * (50 * prob).toInt)
      }.foreach(println)
    }
  }

  def printState(s: QState): Unit =
    printChart(s.bins.map({case (b, v) => (b, v.norm2)}).toMap)

  def main (args: Array[String] ): Unit = {
    def f(x: Int) = x == 5

    grover(f)(3)
  }

  }
