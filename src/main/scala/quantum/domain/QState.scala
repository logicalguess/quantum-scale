package quantum.domain

case class QState(override val bins: List[(Word, Complex)]) extends quantum.computing.QState[Word](bins) {
  override def map(f: Word => Word): QState = {
    QState(super.map(f).bins)
  }

  def flatMap(f: Word => QState): QState = QState(super.flatMap(w => f(w).bins).bins)
  def >>=(f: Word => QState): QState = flatMap(f)

  private val _m = bins.toMap

  def apply(w: Word): Complex = _m.getOrElse(w, Complex.zero)

  def apply(ls: Symbol*): Complex = apply(Word(ls: _*))

  def *(z: Complex): QState = QState(bins.map { case (w, a) => (w, a*z) })

  def unary_- : QState = this * -1.0

  def +(that: QState): QState = QState(combineBinsRule(this.bins ++ that.bins))

  def -(that: QState): QState = this + -that

  // Inner product
  def inner(that: QState): Complex = {
    this.bins.map { case (l, v) => v.conj * that(l) }.foldLeft(Complex.zero)(Complex.plus)
  }

  def <>(that: QState): Complex = this.inner(that)

  // Outer product
  def outer(that: QState): Word => QState = {
    (w: Word) => this * that(w).conj
  }

  def ><(that: QState): Word => QState = this.outer(that)

  def tensor(that: QState): QState = {
    for {
      x <- this
      y <- that
    } yield Word(x.letters ++ y.letters)
  }

}

object QState {
  val sq: Complex = math.sqrt(0.5)

  def pure(w: Word): QState = new QState(List((w, Complex.one)))

  val s0: QState = pure(Word(S0))
  val s1: QState = pure(Word(S1))


  val plus: QState = QState(List(Word(S0) -> sq, Word(S1) -> sq))
  val minus: QState = QState(List(Word(S0) -> sq, Word(S1) -> -sq))
}
