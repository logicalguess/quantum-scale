package quantum.monad

import org.scalatest.FlatSpec

class ProbabilitiesSpec extends FlatSpec {

  implicit def likelihoodFunctionToChange[K](lf: Function[K, Double])(implicit hypos: List[K]): Map[K, List[(K, Double)]] = {
    hypos.map { h => (h, lf(h)) }
    //val z: List[(K, List[(K, Double)])] = Nil
    //ls.foldLeft(z) { case (buffer, (b, v)) => buffer ++ List((b -> List((b -> v)))) }.toMap
  }

  implicit def likelihoodMapToChange[K](ls: List[(K, Double)]): Map[K, List[(K, Double)]] = {
    val z: List[(K, List[(K, Double)])] = Nil
    ls.foldLeft(z) { case (buffer, (b, v)) => buffer ++ List((b -> List((b -> v)))) }.toMap
  }

  def printChart[K](hist: Map[K, Double])(implicit ord: Ordering[K]) {
    def pad(str: String, n: Int): String =
      if (str.length > n) str.substring(0, n) else str + (" " * (n - str.length))

    if (hist.nonEmpty) {
      val keyLen = hist.keys.map(_.toString.length).max
      hist.toSeq.sortBy(_._1).map {
        case (h, prob) =>
          pad(h.toString, keyLen).mkString + " " +
            pad(prob.toString, 6) + " " +
            ("#" * (50 * prob).toInt)
      }.foreach(println)
    }
  }


  "dice" should "dice" in {
    def likelihood(data: Int)(hypo: Int) =
      if (hypo < data) 0.0 else 1.0 / hypo

    val hypos = List(4, 6, 8, 12, 20)

    implicit def dataPointToChange(data: Int) =
      likelihoodFunctionToChange(likelihood(data))(hypos)

    val bins: List[(Int, Double)] = hypos.map { h => (h, 0.2) }
    val prior = new Probabilities[Int]()
    println("Priors:")
    printChart(prior(bins)._1.toMap)

    println()
    println("After a 6 is rolled:")
    val posterior = prior >>= 6
    printChart(posterior(bins)._1.toMap)

    println()
    println("After 6, 8, 7, 7, 5, 4 are rolled after the first 6:")
    //val posterior2 = posterior.sequence(List(6, 8, 7, 7, 5, 4))
    val posterior2 = posterior >>= 6 >>= 8 >>= 7 >>= 7 >>= 5 >>= 4
    printChart(posterior2(bins)._1.toMap)

  }
}

