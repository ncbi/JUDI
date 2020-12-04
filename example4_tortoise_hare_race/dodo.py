from judi import ParamDb, File

racer = ParamDb('racer')
racer.add_param(['tortoise', 'hare'], 'racer')
racer.add_param([1, 2], 'game')

game = ParamDb('game')
game.add_param([1, 2], 'game')

jf_racer = File('timing.csv', param=racer)
jf_game = File('combined_timing.csv', param=game)

class simulate(Task):
    param = racer
    targets = {'out': jf_racer}
    actions = [('cp {}_{}.csv {}', ['#racer', '#game', '$out'])]

class combine(Task):
    param = game
    inputs = {'inp': jf_game}
    targets = {'out': jf_racer}
    actions = [(combine_csvs, ['#inp', '#out'])]
