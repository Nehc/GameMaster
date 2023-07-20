
class Gens:
    @staticmethod
    def sett(ref = None):
        return [ 
        {"role": "system", "content":  " ".join('''You role is to weave the other participants' player-character stories together, control the non-player 
        aspects of the game, create environments in which the players can interact, and solve any game situation. '''.split())},
        {"role": "user", "content": " ".join('''
         To begin, help me create a setting in which everything will happen. Generate a short description of the setting according to the following example: 
        It was the dark middle ages, full of gnomes and zombies. And it was at this time that Darth Vader visited the earth by order of the emperor ...
         Answer concisely, but not too much, Do not write anything about the hero - we will create it later.
        '''.split()) if not ref else " ".join(f'''
         To begin, help me create a setting in which everything will happen. Generate a short description of the setting according to the following example: 
         "It was the dark middle ages, full of gnomes and zombies. And it was at this time that Darth Vader visited the earth by order of the emperor ...", 
         bat base on the following key inputs: {ref}. Answer concisely, but not too much, Do not write anything about the hero - we will create it later. 
        '''.split())} 
        ]
    @staticmethod
    def hero(sett, ref = None):
        return [ 
        {"role": "system", "content": " ".join('''You role is to weave the other participants' player-character stories together, control the non-player 
        aspects of the game, create environments in which the players can interact, and solve any game situation. '''.split())},
        {"role": "user", "content": " ".join(f'''
         Now we need to create the main character. Generate a short description of character, for this:{sett}, 
         according to the following example: Percival was born into a blacksmith's family, he was left without a mother and everything in his life early.
         I'm used to doing it myself. Mind he was close, but the power of God did not offend.  Answer concisely, but not too much.
        '''.split()) if not ref else " ".join(f'''
         Now we need to create the main character. Generate a short description of character, for this:{sett}, 
         according to the following example: "Percival was born into a blacksmith's family, he was left without a mother and everything in his life early.
         I'm used to doing it myself. Mind he was close, but the power of God did not offend.", bat base on the following key inputs: {ref}.  
         Answer concisely, but not too much.
        '''.split())}
        ]
    @staticmethod
    def stats(hero):
        return [ 
        {"role": "system", "content": " ".join('''You role is to weave the other participants' player-character stories together, control the non-player 
        aspects of the game, create environments in which the players can interact, and solve any game situation. '''.split())},
        {"role": "user", "content": " ".join(f'''
         Divide 15 experience points between charisma, strength, and intelligence, based on the following character description: {hero}, 
         Give your answer in the following form:{{character name}}, chr={{charisma points}}, str={{strength points}}, int={{intelligence points}}.
         according to the following example:Persival, chr=5, str=7, int=3. The output should not contain anything else, just name and these three values. 
         Don't write anything else. 
        '''.split())}        ] 
    @staticmethod
    def quest(sett, hero, chr_, str_, int_):
        return [ 
        {"role": "system", "content": " ".join(f'''You role is to weave the other participants' player-character stories together, control the non-player 
        aspects of the game, create environments in which the players can interact, and solve any game situation. This story happened in {sett} with {hero},
        which has this stats: charisma={chr_}, strength={str_}, intelligence={int_}'''.split())},
        {"role": "user", "content": " ".join('''
         You have to help write a scenario of 3-6 events/contacts (these could be obstacles to overcome, enemy to fight, or NPCs to negotiate with in any combination).
         Output the only first scene of the scenario, at the end of answer indicate the following: [{scene number}/{total scenes} in the scenario, {current progress on a scale of 10}/10],
         for example: [1/3,3/10] means the first scene of three, passed on 3 of 10 progress point. Your answer must contain a situation that requires the hero to take additional 
         actions. Answer concisely, but not too much.
        '''.split())}
        ]
    @staticmethod
    def quest_ns(sett, hero, chr_, str_, int_, cur_scene, max_scene, scene):
        return [ 
        {"role": "system", "content": " ".join(f'''You role is to weave the other participants' player-character stories together, control the non-player 
        aspects of the game, create environments in which the players can interact, and solve any game situation. This story happened in {sett} with {hero},
        which has this stats: charisma={chr_}, strength={str_}, intelligence={int_}'''.split())},
        {"role": "user", "content": " ".join(f'''
         You have to help write a scenario of {max_scene} events/contacts (these could be obstacles to overcome, enemy to fight, or NPCs to negotiate with in any combination).
         Before that, the following happened in this scenario: {scene} Since we're starting a new scene - don't forget to reset progress! 
         Output the only current scene (number {cur_scene}) of the scenario, at the end of answer indicate the following: [{{scene number}}/{{total scenes}} in the scenario, {{current progress on a scale of 10}}/10],
         for example: [1/3,3/10] means the first scene of three, passed on 3 of 10 progress point. Your answer must contain a situation that requires the hero to take additional 
         actions. Answer concisely, but not too much.
        '''.split())}
        ]
    @staticmethod
    def quest_roll(sett, hero, chr_, str_, int_, scene, action, scene_num, max_scene_num, q, ans):
        r= [ 
        {"role": "system", "content": " ".join(f'''You role is to weave the other participants' player-character stories together, control the non-player 
        aspects of the game, create environments in which the players can interact, and solve any game situation. This story happened in {sett} with {hero},
        which has this stats: charisma={chr_}, strength={str_}, intelligence={int_}'''.split())},
        {"role": "user", "content": " ".join(f'''
         You have to help write a scenario of {max_scene_num} events/contacts (these could be obstacles to overcome, enemy to fight, or NPCs to negotiate with in any combination).
         {('Before that, the following happened in this scenario:'+scene) if scene else ''} Don't change scen number! It's impotant for postprocess your data. 
         Output the only current scene {scene_num} of the scenario, at the end of answer indicate the following: [{{scene number}}/{{total scenes}} in the scenario, {{current progress on a scale of 10}}/10],
         for example: [1/3,3/10] means the first scene of three, passed on 3 of 10 progress point. Your answer must contain a situation that requires the hero to take additional 
         actions.'''.split())},
         ]
        for i in range(q):
            r.append({"role": "assistant", "content": ans[i-q]})
            r.append({"role": "user", "content": action[i-q]})
        r.append({"role": "user", "content": 'Answer concisely, but not too much. If progress reaches 10 - write 10/10, do not go to the next scene!'})
        return r
    @staticmethod
    def summa(sett, hero, gms, acts, q, re_clear):
        r= [ #{('Before that, the following happened in this scenario:'+summa) if summa else ''}"}]
        {"role": "system", "content": " ".join('''You role is to weave the other participants' player-character stories together, control the non-player 
        aspects of the game, create environments in which the players can interact, and solve any game situation. This story happened in {sett} with {hero}'''.split())}] 
        for i in range(q-1):
            r.append({"role": "assistant", "content": re_clear.sub('',gms[i-q])})
            r.append({"role": "user", "content": re_clear.sub('',acts[i-q+1])})
        r.append({"role": "assistant", "content": re_clear.sub('',gms[-1])})
        r.append({"role": "user", "content": 'Tl;dr all'})
        return r

class SD_Gens:
    @staticmethod
    def sett(sett):
        return [
        {"role": "system", "content": "You are an assistant to a digital artist, helping to synthesize prompts for stable diffusion. Your answer should not contain anything other than the prompt itself."},
        {"role": "user", "content": f"Please create the best prompt for an atmospheric illustration of an RPG setting. Here is a description of the setting: {sett} Remember that prompts for stable diffusion must be strictly in English!"}
        ]
    @staticmethod
    def hero(sett, hero):
        return [
        {"role": "system", "content": "You are an assistant to a digital artist, helping to synthesize prompts for stable diffusion. Your answer should not contain anything other than the prompt itself."},
        {"role": "user", "content": f"Please create the best prompt for an stilistic illustration of an RPG character in {sett}. Here is a description of they: {hero} Remember that prompts for stable diffusion must be strictly in English!"}
        ]
    @staticmethod
    def scene(sett, scene):
        return [
        {"role": "system", "content": "You are an assistant to a digital artist, helping to synthesize prompts for stable diffusion. Your answer should not contain anything other than the prompt itself."},
        {"role": "user", "content": f"Please create the best prompt for an atmospheric illustration of an RPG-game scene {scene} in {sett} Remember that prompts for stable diffusion must be strictly in English!"}
        ]
