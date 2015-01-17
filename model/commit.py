
from datetime import datetime
import mongoengine as me
import os.path

import config
from model.db import database as db
import types
from mongoengine.fields import *
from frc_fields import *

class MatchCommit(me.Document):
    time = me.DateTimeField(default=datetime.now)
    match_num = MatchField(
        # regex=r"^(\d+|\d+\.[12345])$",
        verbose_name = "Match #",
        help_text = "The number of the match scouted",
        # max_length = 5,
        required = True
    )

    match_type = StringField( 
        choices=[("p", "Practice"),("q","Quals"),("qf","Quater Finals"),
                 ("sf","Semi Finals"),("f","Finals")],
        verbose_name = "Match Type",
        help_text = "The type of match scouted",
        default="q",
        required = True,
    )
    event = StringField(
        default = config.event,
        required= "true"
    )

    key = StringField(
        primary_key = True,
        required = True,
        unique = True
    )
    key.to_form_field = types.MethodType(lambda self, model, kwargs: None, key, StringField)

    def clean(self):
        self.key = "{}_{}m{}_{}".format(self.event, self.match_type,
                                       self.match_num, self.team)

    scout = StringField(
        verbose_name = "Scout Name",
        help_text = "The name of the scout",
        max_length = 999,
        required = True
    )
    team = TeamField(
        verbose_name = "Team #",
        help_text = "Identification number of the team scouted",
        required = True
    )
    alliance = StringField(
        verbose_name = "Team's Alliance",
        choices = [('red', 'Red'),('blue', "Blue")],
        help_text = "The alliance of the team scouted, red or blue",
        required = True
    )
    fouls = IntField(
        verbose_name = "Fouls",
        help_text = "How many fouls the team being scouted received",
        min_value = 0,
        default = 0
    )
    tech_fouls = IntField(
         verbose_name = "Technical Fouls",
         help_text = "How many technical fouls the team being scouted received",
         min_value = 0,
         default = 0
    )
    @property
    def foul_contrib(self):
        return -1*(self.fouls * 20 + self.tech_fouls * 50)

    yellow = BooleanField(
         verbose_name = "Yellow Card",
         help_text = "Yellow card received",
         default = False
    )
    red = BooleanField(
         verbose_name = "Red Card",
         help_text = "Did the team being scouted receive a red card?",
         default = False
    )
    comments = StringField(
         verbose_name = "Comments",
         help_text = "Any comments from the scout regarding the team scouted",
         default = ""
    )
    disabled = BooleanField(
         verbose_name = "Disabled",
         help_text = "Was the robot scouted disabled?",
         default = False
    )
    no_show = BooleanField(
         verbose_name = "No Show",
         help_text = 'Was the team scouted a "no show" (not present at the match)',
         default = False
    )

    ###########
    ## Autonomous
    ###########

    tote_bonus = IntField(
        verbose_name = "Tote Bonus",
        help_text= "How many totes did the team push into the scoring zone?",
        max_value = 3,
        min_value = 0,
        default = 0
    )
    @property
    def auto_high_s(self):
        return self.auto_high != 0
        
    bin_bonus = IntField(
        verbose_name = "Bin Bonus",
        help_text = "How many recycle bins did the team push into the scoring zone?",
        max_value = 3,
        min_value = 0,
        default = 0
    )
    @property
    def auto_low_s(self):
        return self.auto_low != 0
    move_bonus = BooleanField(
        verbose_name = "Robot Bonus",
        help_text = "Did the team move into the scoring zone?",
        default = False
    )
    @property
    def auto_hot_s(self):
        return self.auto_hot != 0

    @property
    def auto_contrib(self):
        return sum((
            self.tote_bonus,
        ))

    ###########
    ## Teleop
    ###########
    
    grey_totes_scored = IntField(
        verbose_name =  "Grey Totes",
        help_text =  "The number of grey totes placed into scoring position",
        min_value = 0,
        default = 0
    )
    highest_grey_tote = IntField(
        verbose_name =  "Highest Tote",
        help_text =  "What was the highest tote scored?",
        min_value = 0,
        default = 0
    )
    bins_scored = IntField(
        verbose_name =  "Recycle Bin",
        help_text =  "The number of Recycle Bins Scored",
        min_value = 0,
        default = 0
    )
    highest_bin = IntField(
        verbose_name =  "Highest Bin",
        help_text =  "What was the highest bin scored?",
        min_value = 0,
        less_than = "catch_total",
        default = 0
    )

    litter_landfill = IntField(
        verbose_name =  "Landfill Litter",
        help_text =  "The amount of litter scored in the Landfill",
        min_value = 0,
        less_than = "11",
        default = 0
    )
    litter_thrown = IntField(
        verbose_name =  "Outsourced Litter",
        help_text =  "The number of times the team scouted attempted put litter in the other teams field",
        min_value = 0,
        default = 0
    )
    yellow_totes_scored = IntField(
        verbose_name =  "Yellow Totes",
        help_text =  "The number of times the team scouted placed a yellow tote on the COOP bump.",
        min_value = 0,
        default = 0
    )
    

    @property
    def tele_contrib(self):
        return sum((
            self.grey_totes_scored,
        ))


    #############
    ## Robot Info
    #############
    r_infos = ["tote_pickup", "bin_pickup", "litter_pickup"]
    tote_pickup = BooleanField(
        verbose_name =  "Shooter",
        help_text =  "Did the robot being scouted have a shooter mechanism?",
        default = False
    )
    bin_pickup = BooleanField(
        verbose_name =  "Catcher",
        help_text =  "Did the robot being scouted have a catching mechanism",
        default = False
    )
    litter_pickup = BooleanField(
        verbose_name =  "Pickup",
        help_text =  "Did the robot being scouted have a pickup mechanism?",
        default = False
    )

   
    drive_type = StringField(
        verbose_name =  "Drive Type",
        choices = [("tank", "Tank"), ("strafe", "Strafe")],
        help_text =  "what kind of drive did the robot scouted have?",
        max_length = 999,
        default = ""
    )

    hp = StringField(
        verbose_name =  "Human Player",
        choices = (("",""),("+","+"),("-","-")),
        default = ""
    )


    @property
    def match(self):
        from model import fms
        return fms.Match.objects.with_id("{}_{}m{}".format(
                self.event, self.match_type, self.match_num))
    @property
    def contrib(self):
        return self.auto_contrib + self.tele_contrib
    @property
    def n_hp_f(self):
        return 1 if self.hp == "+" else -1 if self.hp_front == "-" else 0
  
    @property
    def n_hp(self):
        return self.n_hp_f

def parse_cid(cid):
    cid = cid.split("_")
    try:
        e_key, match, team = cid
        match_type, match_num = match.split("m")
    except:
        raise ValueError("Commit id malformated.")
    return (e_key, match_type, match_num, team)

def get_commit(cid):
    # e_key, match_type, match_num, team = parse_cid(cid)
    return MatchCommit.objects.with_id(cid)

# ##############
# # Validators for differnt types
# ##############
# def validate_match(commit):
#   is_team(commit.data['team'])
#   is_match(commit.data['match'])
#   is_true(commit.data['alliance'] in ['red', 'blue'], 'Alliance is not red or blue')
#   try:
#       is_regional(commit.data['regional'])
#   except ex.BadRequest:
#       d = commit.data
#       d['regional'] = config.CURRENT_EVENT
#       commit.data = d


# #####################
# # Validation utils
# #####################
# def is_true(val, exp):
#   if not val:
#       raise ex.BadRequest(exp)

# MATCH_RE = re.compile(r"(p|q|qf|sf|f)(\d+)")
# def looks_like_match(val):
#   match = MATCH_RE.match(val)
#   if match is None:
#       raise ex.BadRequest(str(val) + ' is not a valid match')

# def is_team(team):
#   if not db.sourceTeams.find_one({'team': team}):
#       raise ex.BadRequest(str(team) + ' is not a valid team.')


# def is_regional(regional):
#   if not db.sourceEvent.find_one({'short_name': regional}):
#       raise ex.BadRequest(str(regional) + 'is not a valid regional')
