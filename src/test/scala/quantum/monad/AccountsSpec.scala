package quantum.monad

import org.scalatest.FlatSpec

class AccountsSpec extends FlatSpec {

  "account balances" should "" in {
    val bins: List[(String, Double)] = List("a" -> 2, "b" -> 3, "c" -> 5, "d" -> -8, "e" -> -2)

    val z = new Accounts[String]
    val changeA = List("a" -> -1.0, "b" -> 1.0)
    val changeB = List("b" -> -2.0, "c" -> 1.0, "d" -> 1.0)

    val state = z >>= Map("a" -> changeA, "b" -> changeB, "c" -> Nil, "d" -> Nil, "e" -> Nil)

    assert(state(bins)._1.toSet == Set("a" -> 1.0, "b" -> 2.0, "c" -> 6.0, "d" -> -7.0, "e" -> -2.0))
    println(state.eval(bins))
  }

}
