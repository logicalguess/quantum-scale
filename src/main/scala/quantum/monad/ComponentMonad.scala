package quantum.monad

trait ComponentMonad[I, S, O] extends StateMonad[S, O] { self =>
  def logic: PartialFunction[(I, S), S]
  def transformer: Function[S, O]

  val run = { s: S => (s, transformer(s)) }

  def process(input: I): ComponentMonad[I, S, O] = new ComponentMonad[I, S, O] {
    override def logic: PartialFunction[(I, S), S] = self.logic
    override def transformer: Function[S, O] = self.transformer
    override val run: S => (S, O) = s => {
      val s1 = logic.apply((input, s))
      (s1, transformer(s1))
    }
  }

  def >>=(input: I): ComponentMonad[I, S, O] = new ComponentMonad[I, S, O] {
    override def logic: PartialFunction[(I, S), S] = self.logic
    override def transformer: Function[S, O] = self.transformer
    override val run: S => (S, O) = s => {
      val (s1, a) = self.run(s)
      process(input)(s1)
    }
  }

  def update(input: I): StateMonad[S, Unit] = {
    StateMonad.modify { s: S => logic.apply((input, s)) }
  }

  def update(inputs: List[I]): StateMonad[S, List[Unit]] = StateMonad.sequence[S, Unit](inputs.map(update))

  def sequence(inputs: List[I]): StateMonad[S, List[O]] = StateMonad.sequence(List(this) ++ inputs.map(process))
  def chain(inputs: List[I]): StateMonad[S, O] = StateMonad.chain(List(this) ++ inputs.map(process))

  def traverse(inputs: List[I]): StateMonad[S, List[O]] = StateMonad.traverse(inputs)(process)

}
