table = """
<table class="wikitable">
<tbody>
<tr>
<td>.</td>
<td>sentence (.&nbsp;;&nbsp;? *)</td>
</tr>
<tr>
<td>(</td>
<td>left paren</td>
</tr>
<tr>
<td>)</td>
<td>right paren</td>
</tr>
<tr>
<td>*</td>
<td>not, n't</td>
</tr>
<tr>
<td>--</td>
<td>dash</td>
</tr>
<tr>
<td>,</td>
<td>comma</td>
</tr>
<tr>
<td>:</td>
<td>colon</td>
</tr>
<tr>
<td>ABL</td>
<td>pre-qualifier (quite, rather)</td>
</tr>
<tr>
<td>ABN</td>
<td>pre-quantifier (half, all)</td>
</tr>
<tr>
<td>ABX</td>
<td>pre-quantifier (both)</td>
</tr>
<tr>
<td>AP</td>
<td>post-determiner (many, several, next)</td>
</tr>
<tr>
<td>AT</td>
<td>article (a, the, no)</td>
</tr>
<tr>
<td>BE</td>
<td>be</td>
</tr>
<tr>
<td>BED</td>
<td>were</td>
</tr>
<tr>
<td>BEDZ</td>
<td>was</td>
</tr>
<tr>
<td>BEG</td>
<td>being</td>
</tr>
<tr>
<td>BEM</td>
<td>am</td>
</tr>
<tr>
<td>BEN</td>
<td>been</td>
</tr>
<tr>
<td>BER</td>
<td>are, art</td>
</tr>
<tr>
<td>BEZ</td>
<td>is</td>
</tr>
<tr>
<td>CC</td>
<td>coordinating conjunction (and, or)</td>
</tr>
<tr>
<td>CD</td>
<td>cardinal numeral (one, two, 2, etc.)</td>
</tr>
<tr>
<td>CS</td>
<td>subordinating conjunction (if, although)</td>
</tr>
<tr>
<td>DO</td>
<td>do</td>
</tr>
<tr>
<td>DOD</td>
<td>did</td>
</tr>
<tr>
<td>DOZ</td>
<td>does</td>
</tr>
<tr>
<td>DT</td>
<td>singular determiner/quantifier (this, that)</td>
</tr>
<tr>
<td>DTI</td>
<td>singular or plural determiner/quantifier (some, any)</td>
</tr>
<tr>
<td>DTS</td>
<td>plural determiner (these, those)</td>
</tr>
<tr>
<td>DTX</td>
<td>determiner/double conjunction (either)</td>
</tr>
<tr>
<td>EX</td>
<td>existential there</td>
</tr>
<tr>
<td>FW</td>
<td>foreign word (hyphenated before regular tag)</td>
</tr>
<tr>
<td>HV</td>
<td>have</td>
</tr>
<tr>
<td>HVD</td>
<td>had (past tense)</td>
</tr>
<tr>
<td>HVG</td>
<td>having</td>
</tr>
<tr>
<td>HVN</td>
<td>had (past participle)</td>
</tr>
<tr>
<td>IN</td>
<td>preposition</td>
</tr>
<tr>
<td>JJ</td>
<td>adjective</td>
</tr>
<tr>
<td>JJR</td>
<td>comparative adjective</td>
</tr>
<tr>
<td>JJS</td>
<td>semantically superlative adjective (chief, top)</td>
</tr>
<tr>
<td>JJT</td>
<td>morphologically superlative adjective (biggest)</td>
</tr>
<tr>
<td>MD</td>
<td>modal auxiliary (can, should, will)</td>
</tr>
<tr>
<td>NC</td>
<td>cited word (hyphenated after regular tag)</td>
</tr>
<tr>
<td>NN</td>
<td>singular or mass noun</td>
</tr>
<tr>
<td>NN$</td>
<td>possessive singular noun</td>
</tr>
<tr>
<td>NNS</td>
<td>plural noun</td>
</tr>
<tr>
<td>NNS$</td>
<td>possessive plural noun</td>
</tr>
<tr>
<td>NP</td>
<td>proper noun or part of name phrase</td>
</tr>
<tr>
<td>NP$</td>
<td>possessive proper noun</td>
</tr>
<tr>
<td>NPS</td>
<td>plural proper noun</td>
</tr>
<tr>
<td>NPS$</td>
<td>possessive plural proper noun</td>
</tr>
<tr>
<td>NR</td>
<td>adverbial noun (home, today, west)</td>
</tr>
<tr>
<td>OD</td>
<td>ordinal numeral (first, 2nd)</td>
</tr>
<tr>
<td>PN</td>
<td>nominal pronoun (everybody, nothing)</td>
</tr>
<tr>
<td>PN$</td>
<td>possessive nominal pronoun</td>
</tr>
<tr>
<td>PP$</td>
<td>possessive personal pronoun (my, our)</td>
</tr>
<tr>
<td>PP$$</td>
<td>second (nominal) possessive pronoun (mine, ours)</td>
</tr>
<tr>
<td>PPL</td>
<td>singular reflexive/intensive personal pronoun (myself)</td>
</tr>
<tr>
<td>PPLS</td>
<td>plural reflexive/intensive personal pronoun (ourselves)</td>
</tr>
<tr>
<td>PPO</td>
<td>objective personal pronoun (me, him, it, them)</td>
</tr>
<tr>
<td>PPS</td>
<td>3rd. singular nominative pronoun (he, she, it, one)</td>
</tr>
<tr>
<td>PPSS</td>
<td>other nominative personal pronoun (I, we, they, you)</td>
</tr>
<tr>
<td>PRP</td>
<td>Personal pronoun</td>
</tr>
<tr>
<td>PRP$</td>
<td>Possessive pronoun</td>
</tr>
<tr>
<td>QL</td>
<td>qualifier (very, fairly)</td>
</tr>
<tr>
<td>QLP</td>
<td>post-qualifier (enough, indeed)</td>
</tr>
<tr>
<td>RB</td>
<td>adverb</td>
</tr>
<tr>
<td>RBR</td>
<td>comparative adverb</td>
</tr>
<tr>
<td>RBT</td>
<td>superlative adverb</td>
</tr>
<tr>
<td>RN</td>
<td>nominal adverb (here, then, indoors)</td>
</tr>
<tr>
<td>RP</td>
<td>adverb/particle (about, off, up)</td>
</tr>
<tr>
<td>TO</td>
<td>infinitive marker to</td>
</tr>
<tr>
<td>UH</td>
<td>interjection, exclamation</td>
</tr>
<tr>
<td>VB</td>
<td>verb, base form</td>
</tr>
<tr>
<td>VBD</td>
<td>verb, past tense</td>
</tr>
<tr>
<td>VBG</td>
<td>verb, present participle/gerund</td>
</tr>
<tr>
<td>VBN</td>
<td>verb, past participle</td>
</tr>
<tr>
<td>VBP</td>
<td>verb, non 3rd person, singular, present</td>
</tr>
<tr>
<td>VBZ</td>
<td>verb, 3rd. singular present</td>
</tr>
<tr>
<td>WDT</td>
<td>wh- determiner (what, which)</td>
</tr>
<tr>
<td>WP$</td>
<td>possessive wh- pronoun (whose)</td>
</tr>
<tr>
<td>WPO</td>
<td>objective wh- pronoun (whom, which, that)</td>
</tr>
<tr>
<td>WPS</td>
<td>nominative wh- pronoun (who, which, that)</td>
</tr>
<tr>
<td>WQL</td>
<td>wh- qualifier (how)</td>
</tr>
<tr>
<td>WRB</td>
<td>wh- adverb (how, where, when)</td>
</tr>
</tbody></table>
"""

