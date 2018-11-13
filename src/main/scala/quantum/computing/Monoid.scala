package quantum.computing

trait Monoid[V] {
  val empty: V
  val combine: (V, V) => V
}