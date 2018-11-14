package quantum.domain

abstract sealed class Symbol(val label: String) {
  override def toString = label
}

case object S0 extends Symbol("0")
case object S1 extends Symbol("1")
