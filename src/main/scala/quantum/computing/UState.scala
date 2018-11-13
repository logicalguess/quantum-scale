package quantum.computing

trait UState[+This <: UState[This, B, V], B, V] {
  protected val bins: List[(B, V)]
  protected val m: Monoid[V]

  protected val normalizeStateRule: List[(B, V)] => List[(B, V)] = identity

  protected val combineBinsRule: List[(B, V)] => List[(B, V)] = { bs =>
    bs.groupBy(_._1).toList.map {
      case (b, vs) => (b, vs.map(_._2).foldLeft(m.empty)(m.combine))
    }
  }
  protected val distributionRule: ((B, V), List[(B, V)]) => List[(B, V)]

  def create(bins: List[(B, V)]): This

  def normalize(): This = create(normalizeStateRule(bins))

  def flatMap(f: B => List[(B, V)]): This = {
    val updates: List[(B, V)] = bins.flatMap({ case (b, v) => distributionRule((b, v), f(b)) })
    create(normalizeStateRule(combineBinsRule(updates)))
  }

  def >>=(f: B => List[(B, V)]): This = flatMap(f)
}

