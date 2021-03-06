package quantum.domain

import org.scalacheck.{Arbitrary, Gen}
import org.scalatest.FlatSpec
import org.scalatest.prop.GeneratorDrivenPropertyChecks
import quantum.domain.Gate._
import quantum.domain.QState._

import scala.language.reflectiveCalls

class GateSpec extends FlatSpec with GeneratorDrivenPropertyChecks {
  import Complex._

  implicit val qbits: Arbitrary[QState] = Arbitrary {
    for {
      re0 <- Gen.choose[Double](-99, 99)
      im0 <- Gen.choose[Double](-99, 99)
      re1 <- Gen.choose[Double](-99, 99)
      im1 <- Gen.choose[Double](-99, 99)
    } yield QState(List(Word(S0) -> (re0 + im0.i), Word(S1) -> (re1 + im1.i)))
  }

  "outer product" should "" in forAll { s: QState =>
    val state0 = s >>= (s0 >< s)
    assert(state0(S1) == Complex.zero)
    assert(state0(S1).im == 0.0)

    val state1 = s >>= (s1 >< s)
    assert(state1(S0) == Complex.zero)
    assert(state1(S0).im == 0.0)
  }

  "I|0>" should "be |0>" in {
    val s = I(S0)
    assert(s(S0) == Complex.one)
    assert(s(S1) == Complex.zero)
  }


  "I|1>" should "be |1>" in {
    val s = I(S1)

    assert(s(S0) == Complex.zero)
    assert(s(S1) == Complex.one)
  }


  "H|0>" should "be a multiple of |0> + |1>" in {
    val s = H(S0)
    assert(s(S0) == s(S1))
  }

  "H|1>" should "be a multiple of |0> - |1>" in {
    val s = H(S1)
    assert(s(S0) == -s(S1))
  }

  "The Identity gate" should "preserve amplitudes" in forAll { s: QState =>
    assert((s >>= I) (S0) == s(S0))
    assert((s >>= I) (S1) == s(S1))
  }

  "The NOT gate" should "swap amplitudes" in forAll { s: QState =>
    assert((s >>= X) (S0) == s(S1))
    assert((s >>= X) (S1) == s(S0))
  }

  "X" should "swap the amplitudes of |0> and |1>" in forAll { s: QState =>
    val t: QState = X(s)

    assert(t(S0) == s(S1))
    assert(t(S1) == s(S0))
  }

  "Y" should "swap the amplitudes of |0> and |1>, multiply each amplitude by i, and negate the amplitude of |1>" in forAll { s: QState =>
    val t: QState = Y(s)

    assert(t(S0) == - s(S1) * Complex.i)
    assert(t(S1) == s(S0) * Complex.i)
  }

  "Z" should "negate the amplitude of |1>, leaving the amplitude of |0> unchanged" in forAll { s: QState =>
    val t: QState = Z(s)

    assert(t(S0) == s(S0))
    assert(t(S1) == -s(S1))
  }

  def HZH(s: QState): QState = s >>= H >>= Z >>= H

  "HZH = X" should "be true for any state" in forAll { s: QState =>
    assert(HZH(s)(S0).toString == X(s)(S0).toString)
    assert(HZH(s)(S1).toString == X(s)(S1).toString)
  }

  def ZXY(s: QState): QState = s >>= Y >>= X >>= Z

  "ZXY = i*I" should "be true for any state" in forAll { s: QState =>
    assert(ZXY(s)(S0).toString == (s(S0)*Complex.i).toString)
    assert(ZXY(s)(S1).toString == (s(S1)*Complex.i).toString)
  }

  def XYZ(s: QState): QState = s >>= Z >>= Y >>= X

  "XYZ = i*I" should "be true for any state" in forAll { s: QState =>
    assert(XYZ(s)(S0).toString == (s(S0)*Complex.i).toString)
    assert(XYZ(s)(S1).toString == (s(S1)*Complex.i).toString)
  }

  "Rz(theta)H = HRx(theta)" should "be true for any state" in forAll {  ts: (Double, QState) =>
    val theta = ts._1
    val state = ts._2

    val z: QState = state >>= H >>= Rz(theta)
    val x: QState = state >>= Rx(theta) >>= H

    assert(z(S0).toString == x(S0).toString)
    assert(z(S1).toString == x(S1).toString)
  }

  "HRz(theta) = Rx(theta)H" should "be true for any state" in forAll {  ts: (Double, QState) =>
    val theta = ts._1
    val state = ts._2

    val x: QState = state >>= H >>= Rx(theta)
    val z: QState = state >>= Rz(theta) >>= H

    assert(z(S0).toString == x(S0).toString)
    assert(z(S1).toString == x(S1).toString)
  }

  "Ry(theta)ZRy(-theta)Z = Ry(2*theta)" should "be true for any state" in forAll {  ts: (Double, QState) =>
    val theta = ts._1
    val state = ts._2

    val a: QState = state >>= Z >>= Ry(-theta) >>= Z >>= Ry(theta)
    val b: QState = state >>= Ry(2*theta)

    assert(a(S0).toString == b(S0).toString)
    assert(a(S1).toString == b(S1).toString)
  }

  "Rx(theta)ZRx(-theta)Z = Rx(2*theta)" should "be true for any state" in forAll {  ts: (Double, QState) =>
    val theta = ts._1
    val state = ts._2

    val a: QState = state >>= Z >>= Rx(-theta) >>= Z >>= Rx(theta)
    val b: QState = state >>= Rx(2*theta)

    assert(a(S0).toString == b(S0).toString)
    assert(a(S1).toString == b(S1).toString)
  }

  "Rx(pi/2)|0>" should "= 1/sqrt(2)*|0> - i/sqrt(2)*|1>" in forAll {  theta: Double =>

    val e = s0 >>= Rx(math.Pi/2)

    assert(e(S0).toString == Complex(1/math.sqrt(2), 0).toString)
    assert(e(S1).toString ==  Complex(0, -1/math.sqrt(2)).toString)
  }

  "Rx(-pi/2)|0>" should "= 1/sqrt(2)*|0> + i/sqrt(2)*|1>" in forAll {  theta: Double =>

    val e = s0 >>= Rx(-math.Pi/2)

    assert(e(S0).toString == Complex(1/math.sqrt(2), 0).toString)
    assert(e(S1).toString ==  Complex(0, 1/math.sqrt(2)).toString)
  }

  "R(-pi/2)H|0>" should "= 1/sqrt(2)*|0> - i/sqrt(2)*|1>" in forAll {  theta: Double =>

    val e = s0 >>= H >>= R(-math.Pi/2)

    assert(e(S0).toString == Complex(1/math.sqrt(2), 0).toString)
    assert(e(S1).toString ==  Complex(0, -1/math.sqrt(2)).toString)
  }

  "R(pi/2)H|0>" should "= 1/sqrt(2)*|0> + i/sqrt(2)*|1>" in forAll {  theta: Double =>

    val e = s0 >>= H >>= R(math.Pi/2)

    assert(e(S0).toString == Complex(1/math.sqrt(2), 0).toString)
    assert(e(S1).toString ==  Complex(0, 1/math.sqrt(2)).toString)
  }

  "Z = R(pi)" should "be true for any state" in forAll {  state: QState =>

    val a: QState = state >>= Z
    val b: QState = state >>= R(math.Pi)

    assert(a(S0).toString == b(S0).toString)
    assert(a(S1).toString == b(S1).toString)
  }

  "Ry(theta) eigenvectors" should "are +/-i/sqrt(2)*|0> + 1/sqrt(2)*|1> with eigenvalues cos(theta/2) +/- i*sin(theta/2)" in forAll { theta: Double =>

    // i/sqrt(2)*|0> + 1/sqrt(2)*|1>
    val e1 = s0 >>= Rx(math.Pi/2) >>= Z >>= X

    val a: QState = e1 >>= Ry(theta)
    val b: QState = e1 * Complex(math.cos(theta/2), math.sin(theta/2))

    assert(a(S0).toString == b(S0).toString)
    assert(a(S1).toString == b(S1).toString)

    // -i/sqrt(2)*|0> + 1/sqrt(2)*|1>
    val e2 = s0 >>= Rx(math.Pi/2) >>= X

    val c: QState = e2 >>= Ry(theta)
    val d: QState = e2 * Complex(math.cos(theta/2), -math.sin(theta/2))

    assert(c(S0).toString == d(S0).toString)
    assert(c(S1).toString == d(S1).toString)
  }

  "Rx(theta) eigenvectors" should "are +/-1/sqrt(2)*|0> - 1/sqrt(2)*|1> with eigenvalues cos(theta/2) +/- i*sin(theta/2)" in forAll { theta: Double =>

    // 1/sqrt(2)*|0> - 1/sqrt(2)*|1>
    val e1 = s0 >>= Ry(math.Pi/2) >>= Z
    //val e1 = QState(List(Word(S0)->math.sqrt(0.5), Word(S1)-> -math.sqrt(0.5)))

    val a: QState = e1 >>= Rx(theta)
    val b: QState = e1 * Complex(math.cos(theta/2), math.sin(theta/2))

    assert(a(S0).toString == b(S0).toString)
    assert(a(S1).toString == b(S1).toString)

    // -1/sqrt(2)*|0> - 1/sqrt(2)*|1>
    val e2 = s0 >>= Ry(-math.Pi/2) >>= X >>= Z
    //val e2 = QState(List(Word(S0)-> -math.sqrt(0.5), Word(S1)-> -math.sqrt(0.5)))

    val c: QState = e2 >>= Rx(theta)
    val d: QState = e2 * Complex(math.cos(theta/2), -math.sin(theta/2))

    assert(c(S0).toString == d(S0).toString)
    assert(c(S1).toString == d(S1).toString)
  }

  "H = iRz(pi/2)Rx(pi/2)Rz(pi/2)" should "be true for any state" in forAll {  state:  QState =>

    val h: QState = state >>= H
    val z: QState = state >>= Rz(math.Pi/2) >>= Rx(math.Pi/2) >>= Rz(math.Pi/2)

    assert((z(S0) * Complex.i).toString == h(S0).toString)
    assert((z(S1) * Complex.i).toString == h(S1).toString)
  }

  "Rz(theta)" should "rotate the amplitude of |0> by -theta/2 and the amplitude of |1> by theta/2" in forAll { ts: (Double, QState) =>
    val theta = ts._1
    val state = ts._2

    val z: QState = Rz(theta)(state)

    // Rz rotates the amplitude of |0> by -theta/2
    assert(z(S0) == state(S0) * Complex.one.rot(-theta / 2))
    // Rz rotates the amplitude of |1> by theta/2
    assert(z(S1) == state(S1) * Complex.one.rot(theta / 2))
  }

  "Ry(theta)" should "mix the amplitudes of |0> and |1> (like vector rotation)" in forAll { ts: (Double, QState) =>
    val theta = ts._1
    val state = ts._2

    val y: QState = Ry(theta)(state)

    // same formula as 2-dimensional vector rotation (but with half angle)
    val t0 = state(S0) * math.cos(theta/2) - state(S1) * math.sin(theta/2)
    val t1 = state(S0) * math.sin(theta/2) + state(S1) * math.cos(theta/2)

    assert(y(S0) == t0)
    assert(y(S1) == t1)
  }

  "Ry(theta)(S0)" should "= cos(theta/2)*|0> + sin(theta/2)*|1>" in forAll { theta: Double =>

    val y: QState = Ry(theta)(S0)

    assert(y(S0) == toComplex(math.cos(theta/2)))
    assert(y(S1) == toComplex(math.sin(theta/2)))
  }

  "Ry(pi/2)Z" should "equal H" in forAll { state:  QState =>

    val y: QState = state >>= Z >>= Ry(math.Pi/2)
    val h: QState = state >>= H

    assert(y(S0).toString == h(S0).toString)
    assert(y(S1).toString == h(S1).toString)
  }

  "Ry(pi/2)" should "equal HZ" in forAll { state:  QState =>

    val y: QState = state >>= Ry(math.Pi/2)
    val h: QState = state >>= Z >>= H

    assert(y(S0).toString == h(S0).toString)
    assert(y(S1).toString == h(S1).toString)
  }

  "XRy(pi/2)" should "equal H" in forAll { state:  QState =>

    val y: QState = state >>= Ry(math.Pi/2) >>= X
    val h: QState = state >>= H

    assert(y(S0).toString == h(S0).toString)
    assert(y(S1).toString == h(S1).toString)
  }

  "Ry(pi/2)" should "equal XH" in forAll { state:  QState =>

    val y: QState = state >>= Ry(math.Pi/2)
    val h: QState = state >>= H >>= X

    assert(y(S0).toString == h(S0).toString)
    assert(y(S1).toString == h(S1).toString)
  }

  "Rz(pi)" should "equal -i*Z" in forAll { s: QState =>

    val t: QState = (Z * -Complex.i) (s)
    val r: QState = Rz(math.Pi)(s)

    assert(t(S0).toString == r(S0).toString)
    assert(t(S1).toString == r(S1).toString)
  }

  "R(theta)" should "equal e^(i*theta/2)*Rz(theta)" in forAll { ts: (Double, QState) =>
    val theta = ts._1
    val state = ts._2

    val r: QState = state >>= R(theta)
    val rz: QState = state >>= Rz(theta) * Complex.one.rot((theta/2))

    assert(rz(S0).toString == r(S0).toString)
    assert(rz(S1).toString == r(S1).toString)
  }

  "Rz(theta)" should "equal HRx(theta)H" in forAll { ts: (Double, QState) =>
    val theta = ts._1
    val state = ts._2

    val A: Gate = Rz(theta)
    val B: Gate = H >=> Rx(theta) >=> H

    val a: QState = A(S0)
    val b: QState = B(S0)

    assert((b(S0) - a(S0)).norm2 < 0.1)
    assert((b(S1) - a(S1)).norm2 < 0.1)
  }

  "H" should "create inner product" in forAll { state:  QState =>

    val ns = math.sqrt(state(S0).norm2 + state(S1).norm2)
    val a0 = state(S0).re /ns
    val a1 = state(S0).im /ns
    val b0 = state(S1).re /ns
    val b1 = state(S1).im /ns

    assert((a0*a0 + b0*b0 + a1*a1 + b1*b1 - 1).abs < 0.1)

    val state_n = QState(List(Word(S0) -> Complex(a0, a1), Word(S1) -> Complex(b0, b1)))
    val s: QState = state_n >>= H

    val dot1 = 0.5*(state_n(S0) + state_n(S1)).norm2
    assert((s(S0).norm2 - dot1).norm2 < 0.1)

    val dot = a0*b0 + a1*b1
    assert((s(S0).norm2 - 0.5 - dot).abs < 0.1)
  }

  def dot(a: Complex, b: Complex): Double = {
//    a.re*b.re + a.im*b.im
    (a*b.conj).re
  }

  "H" should "create inner product on 1 qubits" in forAll { s: QState =>
    val norm = math.sqrt(s(S0).norm2 + s(S1).norm2)
    val state_n = QState(List(
      Word(List(S0)) -> s(S0) / norm,
      Word(List(S1)) -> s(S1) / norm
    ))

    val a = state_n(Word(List(S0)))
    val b = state_n(Word(List(S1)))

    val state: QState = state_n >>= wire(0, H)
    val s0 = state(Word(List(S0)))
    assert((s0.norm2 - 0.5 - dot(a, b)).abs < 0.1)
  }

  "H" should "create inner product on 2 qubits" in forAll { s: (QState, QState) =>
    val norm = math.sqrt(s._1(S0).norm2 + s._1(S1).norm2 + s._2(S0).norm2 + s._2(S1).norm2)
    val state_n = QState(List(
      Word(List(S0, S0)) -> s._1(S0) / norm,
      Word(List(S0, S1)) -> s._1(S1) / norm,
      Word(List(S1, S0)) -> s._2(S0) / norm,
      Word(List(S1, S1)) -> s._2(S1) / norm
    ))

    val a00 = state_n(Word(List(S0, S0)))
    val a01 = state_n(Word(List(S0, S1)))
    val a10 = state_n(Word(List(S1, S0)))
    val a11 = state_n(Word(List(S1, S1)))

    val state: QState = state_n >>= wire(0, H)

//    val state = QState(List(
//      Word(List(S0, S0)) -> (a00 + a10)/math.sqrt(2),
//      Word(List(S1, S0)) -> (a00 - a10)/math.sqrt(2),
//      Word(List(S0, S1)) -> (a01 + a11)/math.sqrt(2),
//      Word(List(S1, S1)) -> (a01 - a11)/math.sqrt(2)
//    ))

    val s00 = state(Word(List(S0, S0)))
    val s01 = state(Word(List(S0, S1)))
    val s10 = state(Word(List(S1, S0)))
    val s11 = state(Word(List(S1, S1)))

    assert((s00.norm2 + s01.norm2 + s10.norm2 + s11.norm2 - 1).abs < 0.1)

    val d = dot(a00, a10) + dot(a01, a11)
    assert((s00.norm2 + s01.norm2 - 0.5 - d).abs < 0.1)
//    println((s00.norm2 + s01.norm2 - d).abs)
  }

  "Rz(theta)" should "be a weighted average of I and Rz(pi)" in forAll { ts: (Double, QState) =>
    val theta = ts._1
    val state = ts._2

    val A: Gate = I * math.cos(theta / 2) + Rz(math.Pi) * math.sin(theta / 2)

    val z: QState = Rz(theta)(state)
    val a: QState = A(state)

    assert(z(S0).toString == a(S0).toString)
    assert(z(S1).toString == a(S1).toString)
  }

  "Rz(pi)" should "rotate the amplitude of |0> by -pi/2 and the amplitude of |1> by pi/2" in forAll { s: QState =>

    val z: QState = Rz(math.Pi)(s)

    // Rz rotates the amplitude of |0> by -theta/2
    assert(z(S0) == s(S0) * Complex.one.rot(-math.Pi / 2))
    // Rz rotates the amplitude of |1> by theta/2
    assert(z(S1) == s(S1) * Complex.one.rot(math.Pi / 2))
  }

  "Ry(pi)" should "equal -i*Y" in forAll { s: QState =>

    val t: QState = (Y * -Complex.i) (s)
    val r: QState = Ry(math.Pi)(s)

    assert(t(S0).toString == r(S0).toString)
    assert(t(S1).toString == r(S1).toString)
  }

  "Ry(pi)" should "swap the amplitudes of |0> and |1> and flip the sign of |1> (rotate by pi)" in forAll {
    s: QState =>

      val t: QState = Ry(math.Pi) (s)

      assert(t(S0).toString == (-s(S1)).toString)
      assert(t(S1).toString == s(S0).toString)

    // rotation by pi in a 4-dimensional space (2 complex numbers as components)
    // similar to a rotation by pi/2 in the 2-dimensional case, same as multiplying a complex number by i
    // z = a + bi
    // i*z = -b + ai
  }

  "Ry(theta)" should "be a weighted average of I and Ry(pi)" in forAll { ts: (Double, QState) =>
    val theta = ts._1
    val state = ts._2

    val A: Gate = I * math.cos(theta / 2) + Ry(math.Pi) * math.sin(theta / 2)

    val z: QState = Ry(theta)(state)
    val a: QState = A(state)

    assert(z(S0).toString == a(S0).toString)
    assert(z(S1).toString == a(S1).toString)
  }

  "Rx(pi)" should "equal -i*X" in forAll { s: QState =>

    val t: QState = (X * -Complex.i) (s)
    val r: QState = Rx(math.Pi)(s)

    assert(t(S0).toString == r(S0).toString)
    assert(t(S1).toString == r(S1).toString)
  }

  "Rx(pi)" should "swap the amplitudes of |0> and |1> and rotate them by -pi/2" in forAll { s: QState =>

    val r: QState = Rx(math.Pi)(s)

    assert(r(S0).toString == (s(S1) * Complex.one.rot(-math.Pi/2)).toString)
    assert(r(S1).toString == (s(S0) * Complex.one.rot(-math.Pi/2)).toString)
  }

  "Rx(theta)(S0)" should "cos(theta)*|0> - i*sin(theta/2)*|1>" in forAll { theta: Double =>
    val r: QState = Rx(theta)(S0)

    assert(r(S0) == toComplex(math.cos(-theta/2)))
    assert(r(S1) == math.sin(-theta/2) * Complex.i)
  }

  "Rx(theta)" should "take a*|0> + b*|1> to (a*cos(-theta/2) + i*b*sin(-theta/2))*|0> + (b*cos(-theta/2) + i*a*sin(-theta/2))*|1>" in forAll { ts: (Double, QState) =>
    val theta = ts._1
    val state = ts._2

    val r: QState = Rx(theta)(state)

    val t0 = state(S0) * math.cos(-theta/2) + state(S1) * math.sin(-theta/2) * Complex.i
    val t1 = state(S1) * math.cos(-theta/2) + state(S0) * math.sin(-theta/2) * Complex.i

    assert(r(S0) == t0)
    assert(r(S1) == t1)
  }

  "Rx(theta)" should "be a weighted average of I and Rx(pi)" in forAll { ts: (Double, QState) =>
    val theta = ts._1
    val state = ts._2

    val A: Gate = I * math.cos(theta / 2) + Rx(math.Pi) * math.sin(theta / 2)

    val z: QState = Rx(theta)(state)
    val a: QState = A(state)

    assert(z(S0).toString == a(S0).toString)
    assert(z(S1).toString == a(S1).toString)
  }

  "Rx(pi)Rx(pi)" should "equal -I (quaternion basis)" in forAll { s: QState =>

    val t: QState = Rx(math.Pi)(Rx(math.Pi)(s))

    assert(t(S0).toString == (-s(S0)).toString)
    assert(t(S1).toString == (-s(S1)).toString)
  }

  "Ry(pi)Ry(pi)" should "equal -I (quaternion basis)" in forAll { s: QState =>

    val t: QState = Ry(math.Pi)(Ry(math.Pi)(s))

    assert(t(S0).toString == (-s(S0)).toString)
    assert(t(S1).toString == (-s(S1)).toString)
  }

  "Rz(pi)Rz(pi)" should "equal -I (quaternion basis)" in forAll { s: QState =>

    val t: QState = Rz(math.Pi)(Rz(math.Pi)(s))

    assert(t(S0).toString == (-s(S0)).toString)
    assert(t(S1).toString == (-s(S1)).toString)
  }

  "Rx(pi)Ry(pi)Rz(pi)" should "equal -I (quaternion basis)" in forAll { s: QState =>

    val z: QState = Rz(math.Pi)(s)
    val y: QState = Ry(math.Pi)(z)
    val x: QState = Rx(math.Pi)(y)

    assert(x(S0).toString == (-s(S0)).toString)
    assert(x(S1).toString == (-s(S1)).toString)
  }

  "Rx(pi)Rz(pi)Ry(pi)" should "equal I (quaternion basis)" in forAll { s: QState =>

    val y: QState = Ry(math.Pi)(s)
    val z: QState = Rz(math.Pi)(y)
    val x: QState = Rx(math.Pi)(z)

    assert(x(S0).toString == (s(S0)).toString)
    assert(x(S1).toString == (s(S1)).toString)
  }

  "Rz(pi)Rx(pi)Ry(pi)" should "equal -I (quaternion basis)" in forAll { s: QState =>

    val y: QState = Ry(math.Pi)(s)
    val x: QState = Rx(math.Pi)(y)
    val z: QState = Rz(math.Pi)(x)

    assert(z(S0).toString == (-s(S0)).toString)
    assert(z(S1).toString == (-s(S1)).toString)
  }

  "Z" should "equal i*Rz(pi)" in forAll { s: QState =>

    val t: QState = Z(s)
    val r: QState = (Rz(math.Pi) * Complex.i)(s)

    assert(t(S0).toString == r(S0).toString)
    assert(t(S1).toString == r(S1).toString)
  }

  "I" should "equal Rz(0)" in forAll { s: QState =>

    val t: QState = I(s)
    val r: QState = Rz(0)(s)

    assert(t(S0) == r(S0))
    assert(t(S1) == r(S1))
  }

  "Y" should "equal i*Ry(pi)" in forAll { s: QState =>

    val t: QState = Y(s)
    val r: QState = (Ry(math.Pi) * Complex.i)(s)

    assert(t(S0).toString == r(S0).toString)
    assert(t(S1).toString == r(S1).toString)
  }

  "I" should "equal Ry(0)" in forAll { s: QState =>

    val t: QState = I(s)
    val r: QState = Ry(0)(s)

    assert(t(S0) == r(S0))
    assert(t(S1) == r(S1))
  }

  "X" should "equal i*Rx(pi)" in forAll { s: QState =>

    val t: QState = X(s)
    val r: QState = (Rx(math.Pi) * Complex.i)(s)

    assert(t(S0).toString == r(S0).toString)
    assert(t(S1).toString == r(S1).toString)
  }

  "I" should "equal Rx(0)" in forAll { s: QState =>

    val t: QState = I(s)
    val r: QState = Rx(0)(s)

    assert(t(S0) == r(S0))
    assert(t(S1) == r(S1))
  }

}
