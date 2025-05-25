if __name__ == "__main__":
    # Example usage
    edges = [
        (0, 1, 2),
        (0, 2, 4),
        (1, 2, 1),
        (1, 3, 7),
        (2, 3, 3)
    ]
    source = 0
    app = DijkstraApp(edges, source)
    app.run()