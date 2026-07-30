#this will help visualize the placement of the packages
import plotly.graph_objects as go

def create_figure(uld):
    fig = go.Figure()

    for package in uld.placed_packages:

        x, y, z = package.pos
        l, w, h = package.ori

        fig.add_trace(go.Scatter3d(
            x=[x, x+l, x+l, x, x],
            y=[y, y, y+w, y+w, y],
            z=[z, z, z, z, z],
            mode="lines",
            line=dict(color="blue", width=3),
        ))

        fig.add_trace(go.Scatter3d(
            x=[x, x+l, x+l, x, x],
            y=[y, y, y+w, y+w, y],
            z=[z+h, z+h, z+h, z+h, z+h],
            mode="lines",
            line=dict(color="blue", width=3),
        ))

        corners = [
            (x, y),
            (x+l, y),
            (x+l, y+w),
            (x, y+w),
        ]

        for cx, cy in corners:
            fig.add_trace(go.Scatter3d(
                x=[cx, cx],
                y=[cy, cy],
                z=[z, z+h],
                mode="lines",
                line=dict(color="blue", width=3),
            ))

        fig.add_trace(go.Scatter3d(
            x=[x+l/2],
            y=[y+w/2],
            z=[z+h/2],
            mode="text",
            text=[package.id],
        ))

    fig.update_layout(
        title=f"{uld.id}",
        scene=dict(
            xaxis_title="Length",
            yaxis_title="Width",
            zaxis_title="Height",
        ),
    )

    return fig
def visualize_ulds(ulds):

    for uld in ulds:
        fig = create_figure(uld)
        fig.show()
