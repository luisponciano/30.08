from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import sqlite3
import os
import plotly.grqph_objs as go
from dash import Dash, html, dcc
import dash
import numpy as np
import config
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
#
