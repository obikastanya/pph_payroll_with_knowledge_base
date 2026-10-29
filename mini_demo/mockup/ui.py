"""Look of the mockup: cards, big numbers, badges, step lists. Colours follow the research app (regulation blue,
company orange)."""
import streamlit as st

import glossary

CSS = """
<style>
.block-container { padding-top: 1.4rem; max-width: 1400px; }
div[data-testid="stMetricValue"], div[data-testid="stDataFrame"] { font-variant-numeric: tabular-nums; }
.card { border: 1px solid #e3e2de; border-radius: 12px; padding: 1rem 1.15rem; background: #fff; margin-bottom: .8rem; }
.card h4 { margin: 0 0 .15rem 0; font-size: 1.02rem; }
.card .muted, .muted { color: #6b6a66; font-size: .86rem; }
.big { font-size: 2.1rem; font-weight: 700; letter-spacing: -.02em; font-variant-numeric: tabular-nums; margin: .2rem 0; }
.big.neg { color: #1b7a43; }
.lines { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; margin-top: .4rem; }
.lines, .lines tr, .lines td { border: none !important; background: transparent !important; }
.lines td { padding: .28rem .2rem !important; border-bottom: 1px solid #f0efec !important; vertical-align: top; }
.lines td.r { text-align: right; white-space: nowrap; padding-left: .8rem; }
.lines tr.total td { font-weight: 700; border-top: 2px solid #24231f !important; border-bottom: none !important; }
.lines tr.sub td { color: #6b6a66; font-size: .88rem; }
.lines td.op { width: 1.2rem; color: #6b6a66; }
.badge { display: inline-block; padding: .08rem .5rem; border-radius: 999px; font-size: .76rem; font-weight: 600;
         margin-right: .3rem; }
.b-blue { background: #e8f1fc; color: #1f5fae; } .b-orange { background: #fdeee7; color: #b44a1b; }
.b-green { background: #e6f4ea; color: #1b7a43; } .b-red { background: #fde8e8; color: #b42318; }
.b-grey { background: #f0efec; color: #55544f; } .b-yellow { background: #fff4d6; color: #8a6100; }
.explain { background: #f7f7f5; border-radius: 8px; padding: .55rem .75rem; margin-top: .6rem; font-size: .92rem; }
.step-n { display: inline-block; width: 1.5rem; height: 1.5rem; border-radius: 50%; background: #24231f; color: #fff;
          text-align: center; line-height: 1.5rem; font-size: .8rem; font-weight: 700; margin-right: .45rem; }
.flow { display: flex; gap: .35rem; flex-wrap: wrap; margin: .3rem 0 .6rem 0; }
.flow .s { padding: .3rem .6rem; border-radius: 8px; font-size: .82rem; background: #f0efec; color: #55544f; }
.flow .s.done { background: #e6f4ea; color: #1b7a43; } .flow .s.now { background: #e8f1fc; color: #1f5fae; font-weight: 600; }
.flow .s.fail { background: #fde8e8; color: #b42318; } .flow .s.skip { background: #fff4d6; color: #8a6100; }
.rule { border-left: 4px solid #2a78d6; padding: .5rem .8rem; background: #fafaf8; border-radius: 0 8px 8px 0;
        margin-bottom: .55rem; }
.rule.company { border-left-color: #eb6834; }
.rule.old { border-left-color: #b4b3ae; opacity: .75; }
.quote { font-style: italic; color: #55544f; font-size: .88rem; }
.diff-old { background: #fde8e8; text-decoration: line-through; padding: 0 .25rem; border-radius: 4px; }
.diff-new { background: #e6f4ea; padding: 0 .25rem; border-radius: 4px; font-weight: 600; }
.answer { font-size: 1.02rem; font-weight: 600; margin: .35rem 0 .3rem 0; line-height: 1.45; }
.mock { color: #8a6100; font-size: .8rem; }
</style>
"""


def setup():
    st.markdown(CSS, unsafe_allow_html=True)
    glossary.setup()


def html(text):
    st.markdown(text, unsafe_allow_html=True)


def badge(text, colour="grey"):
    return f'<span class="badge b-{colour}">{text}</span>'


def step(n, title):
    html(f'<div style="margin:.2rem 0 .5rem 0"><span class="step-n">{n}</span><b>{title}</b></div>')


def flow(steps):
    """steps: [(label, state)] with state done | now | fail | skip | todo."""
    html('<div class="flow">' + "".join(f'<span class="s {s}">{label}</span>' for label, s in steps) + "</div>")


def mock(text):
    st.caption(f":orange-badge[Mockup] {text}")
