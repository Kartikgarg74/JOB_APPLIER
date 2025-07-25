// To run: npm install --save-dev @testing-library/react @types/jest jest
import { render, screen } from '@testing-library/react';
import { Button } from '../components/ui/button';
// Jest provides describe/it/expect as globals

describe('Button', () => {
  it('renders the button', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
});
