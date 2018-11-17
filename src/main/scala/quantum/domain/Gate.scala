package quantum.domain

final class Gate(val f: Word => QState) {
  def +(g: Word => QState): Word => QState = (w: Word) => QState(f(w).bins) + QState(g(w).bins)
  def -(g: Word => QState): Word => QState = (w: Word) => QState(f(w).bins) - QState(g(w).bins)
  def *(z: Complex): Word => QState = (w: Word) => f(w) * z
  def >=>(g: Word => QState): Word => QState = w => f(w) >>= g

  def apply(s: QState) = QState(s.flatMap(f).bins)
  def apply(s: Symbol): QState = apply(QState.pure(Word(s)))

}

object Gate {

  import QState._

  implicit def functionToGate(f: Word => QState): Gate = new Gate(f)
  implicit def gateToFunction(op: Gate): Word => QState = op.f

  val ZERO: Gate = (s0 >< s0) //+ (s0 >< s1)

  def I: Gate = {s: Word => pure(s)}

  val X: Gate = (s1 >< s0) + (s0 >< s1)

  val Y: Gate = (s1 * Complex.i >< s0) + (-s0 * Complex.i >< s1)

  val Z: Gate = (s0 >< s0) + (-s1 >< s1)

  val H: Gate = (plus >< s0) + (minus >< s1)

  def Rx(theta: Double): Gate = I * math.cos(theta / 2) - X * Complex.i * math.sin(theta / 2)

  def Ry(theta: Double): Gate = I * math.cos(theta / 2) - Y * Complex.i * math.sin(theta / 2)

  def Rz(theta: Double): Gate = I * math.cos(theta / 2) - Z * Complex.i * math.sin(theta / 2)

  def wire(t: Int, g: Word => QState)(s: Word): QState = {
    s match {
      case Word(Nil) => pure(Word(Nil))
      case Word(h :: rest) if t == 0 => g(h) tensor pure(Word(rest))
      case Word(h :: rest) => pure(Word(h)) tensor wire(t - 1, g)(Word(rest))
    }
  }

  def controlled(c: Int, t: Int, g: Word => QState)(s: Word): QState = {
    controlled(Set(c), t, g)(s)
  }

  def controlled(c: Set[Int], t: Int, g: Word => QState)(s: Word): QState = {
    def reverse(s: Word): QState = {
      pure(Word(s.letters.reverse))
    }

    s match {
      case Word(Nil) => pure(Word(Nil))
      case w if c.isEmpty => wire(t, g)(w)
      case _ if c.contains(t) => throw new Error("target cannot be in the control set")
      case _ if t == 0 => {
        val size = s.letters.size
        controlled(c.map { i => size - 1 - i }, size - 1 - t, g)(Word(s.letters.reverse)) >>= reverse _
      }
      case Word(S0 :: rest) if c.contains(0) => pure(Word(S0 :: rest))
      case Word(S1 :: rest) if c.contains(0) => s1 tensor controlled((c - 0).map { i => i - 1 }, t - 1, g)(Word(rest))
      case Word(h :: rest) if !c.contains(0) => pure(Word(h)) tensor controlled(c.map { i => i - 1 }, t - 1, g)(Word(rest))
    }
  }

  val controlledRy: (Int, Int, Double) => Gate = (c, t, theta) => wire(t, Ry(-theta/2)) _  >=> controlled(c, t, X) _ >=>
    wire(t, Ry(theta/2)) _ >=> controlled(c, t, X) _


}
